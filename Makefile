PYTHON ?= python3
PYTHONPATH := .:packages/vpcm_core/src:packages/vpcm_data/src:packages/vpcm_models/src:packages/vpcm_baselines/src:packages/vpcm_perturbation/src:packages/vpcm_causal/src:packages/vpcm_conformal/src:packages/vpcm_lora/src:packages/vpcm_mechanism/src:packages/vpcm_biomarker/src:packages/vpcm_outcome/src:packages/vpcm_pipeline/src:packages/vpcm_regulatory/src

.PHONY: smoke-test test coverage ruff pyright doi-check

smoke-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_core/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_data/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_models/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_baselines/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_perturbation/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_causal/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_conformal/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_lora/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_mechanism/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_biomarker/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_outcome/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_pipeline/tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s packages/vpcm_regulatory/tests

test:
	PYTHONPATH=$(PYTHONPATH) pytest

coverage:
	PYTHONPATH=$(PYTHONPATH) pytest --cov=vpcm_core --cov=vpcm_data --cov=vpcm_models --cov=vpcm_baselines --cov=vpcm_perturbation --cov=vpcm_causal --cov=vpcm_conformal --cov=vpcm_lora --cov=vpcm_mechanism --cov=vpcm_biomarker --cov=vpcm_outcome --cov=vpcm_pipeline --cov=vpcm_regulatory --cov-report=term-missing --cov-fail-under=85

ruff:
	ruff check .

pyright:
	pyright --project pyproject.toml

doi-check:
	$(PYTHON) scripts/verify_dois.py docs
