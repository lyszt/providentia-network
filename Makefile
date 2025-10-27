# Makefile for Django project

PY ?= python3
PORT ?= 8000
HOST ?= 0.0.0.0
MANAGE = $(PY) manage.py
DJANGO_SETTINGS_MODULE ?= providentia_network.settings
export DJANGO_SETTINGS_MODULE

# Conda convenience variables
CONDA ?= conda
CONDA_ENV ?= providentia-network
ENV_FILE ?= environment.yml

.PHONY: help run makemigrations migrate createsuperuser shell test collectstatic loaddata update

help:
	@echo "Makefile for Django project"
	@echo ""
	@echo "Usage:"
	@echo "  make <target> [VAR=value] - run target"
	@echo ""
	@echo "Targets:"
	@echo "  run                Run development server (default PORT=$(PORT))"
	@echo "  makemigrations     Create new migrations for apps"
	@echo "  migrate            Run Django migrations"
	@echo "  createsuperuser    Create a superuser interactively"
	@echo "  shell              Open Django shell"
	@echo "  test               Run Django tests"
	@echo "  collectstatic      Collect static files (no input)"
	@echo "  loaddata FILE=...  Load fixture FILE (use FILE=path)"
	@echo "  update             Create or update conda environment from $(ENV_FILE)"
	@echo ""

run:
	$(MANAGE) runserver $(HOST):$(PORT)

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

createsuperuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

collectstatic:
	$(MANAGE) collectstatic --noinput

loaddata:
ifndef FILE
	$(error FILE is not set. Use e.g. make loaddata FILE=initial_data.json)
endif
	$(MANAGE) loaddata $(FILE)

# Create or update conda environment from the ENV_FILE. This will create the env if it
# doesn't exist or update (with --prune) if it does. Use: make update [CONDA_ENV=name] [ENV_FILE=path]
update:
	@echo "Updating/creating conda environment '$(CONDA_ENV)' from $(ENV_FILE)..."
	@$(CONDA) env list | grep -qE "(^|[[:space:]])$(CONDA_ENV)([[:space:]]|$$)" && \
	 (echo "found environment '$(CONDA_ENV)', updating..." && $(CONDA) env update -n $(CONDA_ENV) -f $(ENV_FILE) --prune) || \
	 (echo "environment '$(CONDA_ENV)' not found, creating..." && $(CONDA) env create -n $(CONDA_ENV) -f $(ENV_FILE))
	@echo "Done."
