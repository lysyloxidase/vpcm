PYTHON ?= python3
PYTHONPATH := packages/vpcm_core/src:packages/vpcm_data/src:packages/vpcm_models/src:packages/vpcm_baselines/src

.PHONY: smoke-test test coverage ruff pyright doi-check

smoke-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_core/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_data/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_models/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_baselines/tests

test:
	PYTHONPATH=$(PYTHONPATH) pytest

coverage:
	PYTHONPATH=$(PYTHONPATH) pytest --cov=vpcm_core --cov=vpcm_data --cov=vpcm_models --cov=vpcm_baselines --cov-report=term-missing --cov-fail-under=85

ruff:
	ruff check .

pyright:
	pyright --project pyproject.toml

doi-check:
	$(PYTHON) scripts/verify_dois.py docs
