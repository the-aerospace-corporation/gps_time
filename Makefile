.ONESHELL:
SHELL := /bin/bash

SRC = $(wildcard ./nbs/*.ipynb)

all: gps_time test docs

gps_time: $(SRC)
	nbdev_build_lib
	touch gps_time
	# black gps_time

docs_serve: docs
	cd docs && bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs
	pytest --cov-config=.coveragerc --cov-report term-missing --cov=gps_time --profile

release: pypi
	nbdev_bump_version

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist
