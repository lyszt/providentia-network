# Providentia Network — Django backend

This repository contains the Django backend for Providentia Network.

A small Makefile is provided to simplify common development tasks.

Prerequisites
- Python 3 (the Makefile defaults to `python3`).
- A virtual environment or Conda environment is recommended. There's an `environment.yml` available if you use Conda.

Quick examples

- Show available targets:

  make help

- Run the development server (default: 0.0.0.0:8000):

  make run

  or customize host/port:

  make run PORT=8080 HOST=127.0.0.1

- Create and apply migrations:

  make makemigrations
  make migrate

- Create a superuser:

  make createsuperuser

- Open Django shell:

  make shell

- Run tests:

  make test

- Collect static files (non-interactive):

  make collectstatic

- Load a fixture:

  make loaddata FILE=fixtures/initial_data.json

Customizing the Python interpreter or settings
- To use a specific Python executable (for example a virtualenv's python), set the `PY` variable:

  make run PY=~/.venvs/myenv/bin/python

- The Makefile exports `DJANGO_SETTINGS_MODULE` and defaults to `providentia_network.settings`. To use a different settings module:

  make run DJANGO_SETTINGS_MODULE=myproject.settings.dev

Notes
- The Makefile aims to be small and unobtrusive — feel free to add project-specific targets (lint, format, coverage, docker, etc.).
- If you rely on Conda, create the environment with the included `environment.yml`:

  conda env create -f environment.yml
  conda activate <env-name>

That's it — use `make help` to see the targets and examples above.
