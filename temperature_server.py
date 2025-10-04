from flask import Flask, render_template_string, Response, request
import Adafruit_DHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, csv, os, threading, time
from datetime import datetime, date
import pandas as pd
import numpy as np

app = Flask(__name__)

# ====== CONFIG ======
SENSOR = Adafruit_DHT.DHT11
PINS = {
    "Sensor 1 (GPIO4)": 4,
    "Sensor 2 (GPIO24)": 24
}
LOG_INTERVAL = 60  # seconds
DATA_DIR = "data"
TEMPERATURE_OFFSET = -4 # Temperature offset to compensate for sensor innacuracy
# ====================

os.makedirs(DATA_DIR, exist_ok=True)

# HTML template with table + plot + date selector
HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Raspberry Pi Station</title>
  <meta http-equiv="refresh" content="120">
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; }
    table { margin: auto; border-collapse: collapse; font-size: 1.4em; }
    th, td { border: 1px solid #444; padding: 12px 24px; }
    th { background-color: #f0f0f0; }
    .err { color: #b00; }
    .date-box { margin: 30px; font-size: 1.5em; }
    .date-box input[type="date"] {
      font-size: 1.2em;
      padding: 8px 12px;
      margin-left: 10px;
    }
    .date-box input[type="submit"] {
      font-size: 1.2em;
      padding: 8px 20px;
      margin-left: 10px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1 style="font-size:2.2em;">Temperature & Humidity</h1>
  <table>
    <tr>
      <th>Sensor</th>
      <th>Temperature (°C)</th>
      <th>Humidity (%)</th>
    </tr>
    {% for name, t, h in sensor_data %}
    <tr>
      <td>{{ name }}</td>
      <td>{% if t == "Error" %}<span class="err">Error</span>{% else %}{{ t }}{% endif %}</td>
      <td>{% if h == "Error" %}<span class="err">Error</span>{% else %}{{ h }}{% endif %}</td>
    </tr>
    {% endfor %}
    <tr>
      <th>Average</th>
      <th>{{ avg_temp }}</th>
      <th>{{ avg_hum }}</th>
    </tr>
  </table>
  <h3> Sensor offset: {{TEMPERATURE_OFFSET}} ºC</h3>

  <div class="date-box">
    <form method="get" action="/">
      <label for="date"><b>Select date:</b></label>
      <input type="date" id="date" name="date" value="{{ selected_date }}">
      <input type="submit" value="Show">
    </form>
  </div>

  <h2 style="font-size:2em;">Daily Average Plot</h2>
  <img src="/plot.png?date={{ selected_date }}" alt="Daily Plot" width="900">

  <p style="font-size:1.2em;">(auto-refresh every 120s, plot updates too)</p>
</body>
</html>
"""

def csv_filename(day):
    return os.path.join(DATA_DIR, f"{day}.csv")

def log_to_csv(temp, hum):
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M")
    with open(csv_filename(today), "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, now, temp, hum])

def load_day_data(day):
    fname = csv_filename(day)
    if not os.path.exists(fname):
        return pd.DataFrame(columns=["date", "time", "temp", "hum"])
    df = pd.read_csv(fname, names=["date", "time", "temp", "hum"])
    return df[df["date"] == day]

def read_sensors():
    """Read all sensors, return list of (name, temp, hum), avg_temp, avg_hum"""
    sensor_data = []
    temps, hums = [], []
    for name, pin in PINS.items():
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, pin)
        if humidity is None or temperature is None:
            t, h = "Error", "Error"
        else:
            t, h = round(temperature, 1) + TEMPERATURE_OFFSET, round(humidity, 1)
            temps.append(t)
            hums.append(h)
        sensor_data.append((name, t, h))
    if temps and hums:
        avg_temp = round(sum(temps)/len(temps), 1)
        avg_hum = round(sum(hums)/len(hums), 1)
    else:
        avg_temp, avg_hum = "Error", "Error"
    return sensor_data, avg_temp, avg_hum

def background_logger():
    """Thread that logs data every LOG_INTERVAL seconds"""
    while True:
        sensor_data, avg_temp, avg_hum = read_sensors()
        if avg_temp != "Error" and avg_hum != "Error":
            log_to_csv(avg_temp, avg_hum)
        time.sleep(LOG_INTERVAL)

@app.route("/")
def index():
    selected_date = request.args.get("date", date.today().isoformat())
    sensor_data, avg_temp, avg_hum = read_sensors()
    return render_template_string(
        HTML,
        sensor_data=sensor_data,
        avg_temp=avg_temp,
        avg_hum=avg_hum,
        selected_date=selected_date,
        TEMPERATURE_OFFSET=TEMPERATURE_OFFSET
    )

@app.route("/plot.png")
def plot_png():
    day = request.args.get("date", date.today().isoformat())
    df = load_day_data(day)
    fig, ax1 = plt.subplots(figsize=(10, 4))

    # Fixed X-axis (0–24h)
    ax1.set_xlim(0, 24)
    ax1.set_xlabel("Hour of Day", fontsize=14)
    ax1.tick_params(axis="x", labelsize=13)
    ax1.set_xticks(np.arange(0, 25, 1))  # show every 2 hours

    # Left Y-axis for Temperature
    ax1.set_ylim(15, 26)
    ax1.set_ylabel("Temperature (°C)", color="red", fontsize=16)
    ax1.tick_params(axis="y", labelsize=13, colors="red")

    if not df.empty:
        df["hour"] = df["time"].apply(lambda x: int(x.split(":")[0]) + int(x.split(":")[1])/60)
        ax1.plot(df["hour"], df["temp"], color="red", marker="o", label="Temperature")

    # Right Y-axis for Humidity
    ax2 = ax1.twinx()
    ax2.set_ylim(30, 70)
    ax2.set_ylabel("Humidity (%)", color="blue", fontsize=16)
    ax2.tick_params(axis="y", labelsize=13, colors="blue")

    if not df.empty:
        ax2.plot(df["hour"], df["hum"], color="blue", marker="x", label="Humidity")

    # Shadow Grid
    ax1.grid(
        True, which="both", axis="both",
        linestyle="--", linewidth=0.7,
        color="gray", alpha=0.5
    )

    fig.tight_layout()
    output = io.BytesIO()
    plt.savefig(output, format="png")
    plt.close(fig)
    output.seek(0)
    return Response(output.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    t = threading.Thread(target=background_logger, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)

