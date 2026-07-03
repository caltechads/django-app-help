RAWVERSION = $(filter-out __version__ = , $(shell grep __version__ app_help/__init__.py))
VERSION = $(strip $(shell echo $(RAWVERSION)))

PACKAGE = django-app-help

clean::
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'
	find . -name "__pycache__" -exec rm -rf '{}' ';'

version::
	@echo $(VERSION)

dist:: clean
	@python -m build

pypi: dist
	@twine upload dist/*

release: pypi
	@bin/release.sh

tox:
	@tox

