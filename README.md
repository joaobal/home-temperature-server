# My Project Template

This is a template for new projects.

## Getting Started

1.  Create a new repository from this template.
2.  Clone your new repository.
3.  Manually create the `dev` branch:
    ```bash
    git checkout -b dev
    git push --set-upstream origin dev
    git checkout master
    ```
4.  Follow the project-specific setup instructions below.

## Branching Strategy

GitFlow:

- master: This branch always reflects a production-ready state. Only release-ready code is merged here.
- dev: This is the primary development branch where all completed features are merged. It represents the latest delivered development changes for the next release.
- feature/*: These branches are created from dev for working on new features. They are merged back into dev when the feature is complete.
- release/*: When dev has enough features for a release (or a release date is approaching), a release branch is created from dev. This branch is used for final testing, bug fixes, and preparing release metadata. Once ready, it's merged into master (and tagged) and also back into dev (to incorporate any bug fixes made in the release branch).
- hotfix/: These branches are created from master to quickly patch production issues. Once fixed, the hotfix is merged back into both master and dev (or the current release branch).

## Further Setup
(Add any further instructions here)
