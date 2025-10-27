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

Conda convenience: update target

A single Makefile target, `update`, creates or updates a Conda environment from the repository's `environment.yml`.

Usage

- Create or update the default env (name taken from the Makefile, defaults to `providentia-network`):

  make update

- Specify a different environment name or environment file:

  make update CONDA_ENV=my-env-name
  make update ENV_FILE=envs/dev-environment.yml

- Use a specific conda binary (for example micromamba or a conda in a custom location):

  make update CONDA=~/.local/bin/micromamba

What the target does

- If the environment named by `CONDA_ENV` exists, the target runs `conda env update -n <name> -f <ENV_FILE> --prune` to update it.
- If the environment does not exist, the target runs `conda env create -n <name> -f <ENV_FILE>` to create it.

Notes

- `conda` must be available on PATH (or set `CONDA` to a full path). If you're using `micromamba` or a different installer, set `CONDA` accordingly.
- The Makefile uses `ENV_FILE` (default `environment.yml`) as the environment spec. Update that file to include any packages you need.

That's it — run `make update` from the project root to ensure your Conda environment matches the repository spec.

That's it — use `make help` to see the targets and examples above.
