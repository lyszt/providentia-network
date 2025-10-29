
.PHONY: prepare update run

prepare:
	conda env create -f environment.yml

update:
	conda env update --file environment.yml --prune

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate
