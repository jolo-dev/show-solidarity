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
	cd website && npm install

test:
	$(PYTHON) -m pytest -o log_cli_level=INFO -W ignore::DeprecationWarning -s -v tests

synth:
	cd infrastructure && npx aws-cdk synth && CDK_DEFAULT_ACCOUNT=$(CDK_DEFAULT_ACCOUNT) npx aws-cdk bootstrap --profile $(CDK_DEFAULT_PROFILE)

infra:
	cd infrastructure && CDK_DEFAULT_ACCOUNT=$(CDK_DEFAULT_ACCOUNT) npx aws-cdk deploy --profile $(CDK_DEFAULT_PROFILE) --require-approval never --outputs-file outputs.json

destroy_infra:
	cd infrastructure && npx aws-cdk destroy --force

website: infra
	cd website && \
	VITE_BUCKET_NAME=$(shell aws cloudformation describe-stacks --stack-name S3ImageLambdaStack --profile $(CDK_DEFAULT_PROFILE) | jq -r ".Stacks[].Outputs[] | select(.OutputKey==\"BucketName\") | .OutputValue") \
	VITE_AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	VITE_AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	npm run dev

all: install synth infra website

clean:
	rm -rf .pytest_cache **/__pycache__ **/cdk.out

.PHONY: install test lint fmt synth clean infra website