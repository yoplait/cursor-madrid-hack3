VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
LIBREYOLO_DIR := vendor/libreyolo
export PYTHONPATH := src

.PHONY: setup verify detect segment backend frontend dev clean-runs

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "$(LIBREYOLO_DIR)[rfdetr]"
	$(PIP) install -r src/backend/requirements.txt

verify:
	$(PYTHON) -c "from libreyolo import LibreYOLO; print('LibreYOLO ready')"

detect:
	cd $(LIBREYOLO_DIR) && ../../$(PYTHON) ../../src/model/detect.py

segment:
	cd $(LIBREYOLO_DIR) && ../../$(PYTHON) ../../src/model/segment.py

backend:
	$(PYTHON) -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	$(PYTHON) -m http.server 8080 --directory src/frontend

dev:
	chmod +x scripts/dev.sh
	./scripts/dev.sh

clean-runs:
	rm -rf $(LIBREYOLO_DIR)/runs
