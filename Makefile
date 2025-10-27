# Makefile for Django project

PY ?= python3
PORT ?= 8000
HOST ?= 0.0.0.0
MANAGE = $(PY) manage.py
DJANGO_SETTINGS_MODULE ?= providentia_network.settings
export DJANGO_SETTINGS_MODULE

.PHONY: help run makemigrations migrate createsuperuser shell test collectstatic loaddata

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

