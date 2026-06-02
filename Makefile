VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
LIBREYOLO_DIR := vendor/libreyolo

.PHONY: setup verify detect segment clean-runs

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "$(LIBREYOLO_DIR)[rfdetr]"

verify:
	$(PYTHON) -c "from libreyolo import LibreYOLO; print('LibreYOLO ready')"

detect:
	cd $(LIBREYOLO_DIR) && ../../$(PYTHON) ../../src/model/detect.py

segment:
	cd $(LIBREYOLO_DIR) && ../../$(PYTHON) ../../src/model/segment.py

clean-runs:
	rm -rf $(LIBREYOLO_DIR)/runs
