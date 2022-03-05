VENV := .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
VENV_ACTIVATE=python3 -m venv $(VENV) && . $(VENV)/bin/activate

# venv is a shortcut target
venv: $(VENV)/bin/activate

pip_update:
	$(VENV_ACTIVATE) && $(PIP) install --upgrade pip

install: pip_update venv
	pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -o log_cli_level=INFO -W ignore::DeprecationWarning -s -v tests

clean:
	rm -rf **/.pytest_cache **/__pycache__

.PHONY: install test lint fmt synth clean