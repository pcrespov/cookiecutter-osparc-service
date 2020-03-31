#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
SHELL = /bin/bash
.DEFAULT_GOAL := help

OUTPUT_DIR = $(CURDIR)/.output
TEMPLATE = $(CURDIR)

#-----------------------------------
.PHONY: devenv
.venv:
	python3 -m venv $@
	# upgrading package managers
	$@/bin/pip install --upgrade \
		pip \
		wheel \
		setuptools
	# tooling
	$@/bin/pip install pip-tools

requirements.txt: .venv requirements.in
	# freezes requirements
	$</bin/pip-compile --upgrade --build-isolation --output-file $@ $(word2, $^)

devenv: .venv requirements.txt ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	@$</bin/pip3 install -r  $(word 2,$^)
	# your dev environment contains
	@$</bin/pip3 list
	@echo "To activate the virtual environment, run 'source $</bin/activate'"


.PHONY: tests
tests: ## tests backed cookie
	@pytest -vv \
		--basetemp=$(CURDIR)/tmp \
		--exitfirst \
		--failed-first \
		--durations=0 \
		--pdb \
		$(CURDIR)/tests


#-----------------------------------
.PHONY: play

$(OUTPUT_DIR):
	# creating $@
	@mkdir -p $@

define cookiecutterrc =
$(shell find $(OUTPUT_DIR) -name ".cookiecutterrc" 2>/dev/null | tail -n 1 )
endef


play: $(OUTPUT_DIR) ## runs cookiecutter into output folder
ifeq (,$(cookiecutterrc))
	# baking cookie $(TEMPLATE) onto $<
	@cookiecutter --output-dir "$<" "$(TEMPLATE)"
else
	# replaying cookie-cutter using $(cookiecutterrc)
	@cookiecutter --no-input -f \
		--config-file="$(cookiecutterrc)"  \
		--output-dir="$<" "$(TEMPLATE)"
endif
	@echo "To see generated code, lauch 'code $(OUTPUT_DIR)'"



.PHONY: version-patch version-minor version-major
version-patch version-minor version-major: ## commits version as patch (bug fixes not affecting the API), minor/minor (backwards-compatible/INcompatible API addition or changes)
	# upgrades as $(subst version-,,$@) version, commits and tags
	@bump2version --verbose  --list $(subst version-,,$@)


#-----------------------------------
.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

git_clean_args = -dxf --exclude=.vscode/ --exclude=.venv/

.PHONY: clean clean-force
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)
	-rm -rf $(OUTPUT_DIR)

clean-force: clean
	# removing .venv
	-@rm -rf .venv
