# Home Temperature Server

Temperature and humidity measurement and analysis server. Tested on an RPi connected to two DHT11 sensors.

<div align="center">
    <img width="600" alt="image" src="https://github.com/user-attachments/assets/f6829f3d-97c3-4e5d-99d0-b380b7206714" />
</div>

## Dependencies

```
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev python3-matplotlib
pip3 install flask Adafruit_DHT pandas numpy
```

## Start server

Simply run the script
```
python3 temperature_server.py 
```

Or create a systemd service as shown in section "Start on boot".

## View data

Go to http://\<ip-of-device-running-server\>:5000/

## Start on boot

Create .service file in `/etc/systemd/system/dht11.service`:
```
[Unit]
Description=DHT11 Temperature & Humidity Reader
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/Code/temp-sensor/temperature_server_v2.py
WorkingDirectory=/home/pi/Code/temp-sensor
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Reload the daemon and start the service:

```
sudo systemctl daemon-reload
sudo systemctl enable dht11.service
sudo systemctl start dht11.service
```

## Reset data:

Remove contents of data/ folder, where there is a csv for each day of data.

```
rm data/*
```

