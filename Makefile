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
	cd website && pnpm install

test:
	$(PYTHON) -m pytest -o log_cli_level=INFO -W ignore::DeprecationWarning -s -v tests

synth: venv
	cd infrastructure \
	&& npx aws-cdk synth --profile $(AWS_PROFILE) \
	&& CDK_DEFAULT_ACCOUNT=$(shell aws sts get-caller-identity --profile $$AWS_PROFILE | jq -r ".Account") npx aws-cdk bootstrap --profile $(AWS_PROFILE)

infra: venv
	cd infrastructure \
	&& CDK_DEFAULT_ACCOUNT=$(shell aws sts get-caller-identity --profile $$AWS_PROFILE | jq -r ".Account") npx aws-cdk deploy --profile $(AWS_PROFILE) --require-approval never

destroy_infra: venv
	cd infrastructure && npx aws-cdk destroy --force

website: venv infra
	cd website && \
	VITE_SOURCE_BUCKET_NAME=$(shell aws cloudformation --profile $$AWS_PROFILE describe-stacks --stack-name SolidarityImageStack | jq -r ".Stacks[].Outputs[] | select(.OutputKey | startswith(\"SourceSolidarityImageBucketBucketName\")) | .OutputValue") \
	VITE_RESULT_BUCKET_NAME=$(shell aws cloudformation --profile $$AWS_PROFILE describe-stacks --stack-name SolidarityImageStack | jq -r ".Stacks[].Outputs[] | select(.OutputKey | startswith(\"ResultSolidarityImageBucketBucketName\")) | .OutputValue") \
	pnpm run dev

all: install synth infra website

clean:
	rm -rf .pytest_cache **/__pycache__ **/cdk.out

.PHONY: install test lint fmt synth clean infra website
