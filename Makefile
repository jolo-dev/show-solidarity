VENV := .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
VENV_ACTIVATE=python3 -m venv $(VENV) && . $(VENV)/bin/activate

# venv is a shortcut target
venv: $(VENV)/bin/activate

pip_update:
	$(VENV_ACTIVATE) && $(PIP) install --upgrade pip

install: pip_update venv
	$(PIP) install -r requirements-dev.txt
	cd website && npm install

test:
	$(PYTHON) -m pytest -o log_cli_level=INFO -W ignore::DeprecationWarning -s -v tests

synth:
	cd infrastructure \
	&& npx aws-cdk synth \
	&& CDK_DEFAULT_ACCOUNT=$(shell aws sts get-caller-identity | jq -r ".Account") npx aws-cdk bootstrap

infra: venv
	cd infrastructure \
	&& CDK_DEFAULT_ACCOUNT=$(shell aws sts get-caller-identity --profile jolo | jq -r ".Account") npx aws-cdk deploy --profile jolo --require-approval never

destroy_infra: venv
	cd infrastructure && npx aws-cdk destroy --force

website: venv infra
	cd website && \
	VITE_SOURCE_BUCKET_NAME=$(shell aws cloudformation describe-stacks --stack-name SolidarityImageStack | jq -r ".Stacks[].Outputs[] | select(.OutputKey | startswith(\"SourceSolidarityImageBucketBucketName\")) | .OutputValue") \
	VITE_RESULT_BUCKET_NAME=$(shell aws cloudformation describe-stacks --stack-name SolidarityImageStack | jq -r ".Stacks[].Outputs[] | select(.OutputKey | startswith(\"ResultSolidarityImageBucketBucketName\")) | .OutputValue") \
	VITE_AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	VITE_AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	VITE_AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
	npm run dev

all: install synth infra website

clean:
	rm -rf .pytest_cache **/__pycache__ **/cdk.out

.PHONY: install test lint fmt synth clean infra website
