SHELL = /bin/bash

##
# Definitions.

.SUFFIXES:

VENV_DIR = $(CURDIR)/.venv
OUTPUT_DIR = $(CURDIR)/output
TEMPLATE = $(CURDIR)

## Tools
tools =

ifeq ($(shell uname -s),Darwin)
	SED = gsed
else
	SED = sed
endif

ifeq ($(shell which ${SED}),)
	tools += $(SED)
endif


## -------------------------------
# All.

all: help
ifdef tools
	$(error "Can't find tools:${tools}")
endif


#-----------------------------------
.PHONY: install
# target: install – installs all tooling to run and test current cookie-cutter
install: venv
	@. "$(VENV_DIR)/bin/activate" && pip install -r requirements.txt


#-----------------------------------
$(OUTPUT_DIR):
	@mkdir -p $(OUTPUT_DIR)/packages
	@mkdir -p $(OUTPUT_DIR)/services
	. "$(VENV_DIR)/bin/activate" && cookiecutter --output-dir "$(OUTPUT_DIR)/services" "$(TEMPLATE)"

.PHONY: run play
# target: run – runs cookiecutter into output folder
run: install $(OUTPUT_DIR)
	@touch .tmp-ran

play: run
.tmp-ran: run


#-----------------------------------
.PHONY: replay
# target: replay – replays cookiecutter in output directory
replay: .tmp-ran
	@. "$(VENV_DIR)/bin/activate" && \
		cookiecutter --no-input -f \
			--config-file="$(shell find $(OUTPUT_DIR) -name ".cookiecutterrc" | tail -n 1)"  \
			--output-dir="$(OUTPUT_DIR)/services" "$(TEMPLATE)"

#-----------------------------------
.PHONE: test
# target: test – tests backed cookie
test: install
	@. "$(VENV_DIR)/bin/activate" && pytest -s -c $(CURDIR)/pytest.ini

#-----------------------------------
$(VENV_DIR):
	@python3 -m venv "$(VENV_DIR)"
	@"$(VENV_DIR)/bin/pip3" install --upgrade pip wheel setuptools
	@echo "To activate the virtual environment, execute 'source $(VENV_DIR)/bin/activate'"

.PHONY: venv
# target: venv – Create the virtual environment into venv folder
venv: $(VENV_DIR)
.venv: $(VENV_DIR)


.PHONY: requirements
# target: requirements – Pip compile requirements.in
requirements: requirements.in
	@pip install pip-tools
	@pip-compile -v --output-file requirements.txt requirements.in
	@touch requirements.txt



## -------------------------------
# Auxiliary targets.

.PHONY: help
# target: help – Display all callable targets
help:
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| $(SED) -r "s/^\s*#\s*target\s*:\s*//g"
	@echo


.PHONY: clean
# target: clean – cleans projects directory
clean:
	@find "$(CURDIR)" \
		-name "*.py[cod]" -exec rm -fv {} + -o \
		-name __pycache__ -exec rm -rfv {} +
	@rm -rfv \
		"$(CURDIR)/.cache" \
		"$(CURDIR)/.mypy_cache" \
		"$(CURDIR)/.pytest_cache"
	@rm -rf "$(OUTPUT_DIR)"

# target: clean-force – cleans & removes also venv folder
clean-force: clean
	@rm -rf "$(VENV_DIR)"
