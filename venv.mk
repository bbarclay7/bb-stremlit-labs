SHELL := /bin/bash
python_exe ?= /opt/homebrew/bin/python3
localdir ?= local
pips ?= pyyaml mako osascript

# turn off time-wasting implicit make stuff
.SUFFIXES:
%:: RCS/%,v
%:: RCS/%
%:: s.%
%:: SCCS/s.%
RCS_REVISION=


ifneq (,$(VIRTUAL_ENV))
$(error VIRTUAL_ENV env var is set; this Makefile requires no pre-existing venv setup)
endif
with_venv := source local/venv/bin/activate &&

#MENU menu: show this menu
menu:
	@cat $(PWD)/Makefile $(PWD)/venv.mk | perl -n -e 'print if s/^(\S+):[^#]+#(.*)?/\1:\2/'
	@cat $(PWD)/Makefile $(PWD)/venv.mk | grep '^#MENU ' | sed 's/^#MENU //'



# standard_gitignores will be added to .gitignore file if not already present
# on initial make
# escape #'s and other perl-regex special characters
standard_gitignores = \#per-project-items $(localdir) *~ aside results bad* *.log \\\#\\\#* .\\\#*

#this macro, when called, emits recipe to add argument to $PWD/.gitignore idempotently
define GITIGNORE_MACRO
	@if [[ ! -e .gitignore ]]; then touch .gitignore; fi

	@if ! grep -qxF "$(1)" .gitignore; then \
	   echo "added $(1) to .gitignore" ;\
	   echo "$(1)" >> .gitignore ;\
	fi

endef

tf=$(localdir)/touchfiles
$(tf)/tf:
	mkdir -p $(tf)
	$(foreach i,$(standard_gitignores),$(call GITIGNORE_MACRO,$(i)))
	touch $@

reset-%: | $(tf)/tf
	@rm -f $(tf)/$*

re-%: | $(tf)/tf
	@rm -f $(tf)/$* >& /dev/null
	@make $(tf)/$*

do-%: | $(tf)/tf
	@make reset-$* >& /dev/null
	@make $(tf)/$*

$(tf)/standard_gitignores:
	$(foreach i,$(standard_gitignores),$(call GITIGNORE_MACRO,$(i)))
	touch $@

$(tf)/python3-exists: $(tf)/tf
	which $(python_exe)
	touch $@

$(tf)/venv: $(tf)/python3-exists $(tf)/standard_gitignores
	$(python_exe) -m venv $(localdir)/venv
	$(with_venv) pip $(pipargs) install --upgrade pip
	$(with_venv) pip $(pipargs) install --upgrade $(pips)
	touch $@

venv: $(tf)/venv

#MENU init: initialize venv, etc..
init: $(tf)/venv

#MENU example.py: create sample python with correct relocatable shebang to use venv
example.py: venv
	echo '#!/bin/bash' > $@
	echo '# -*- Mode: Python; coding: utf-8; -*-' >> $@
	echo '# vim: syn=python' >> $@
	echo '"exec" "$$(dirname $$0)/$(localdir)/venv/bin/python3" "$$0" "$$@"' >>$@
	chmod +x $@


#MENU pips: install (and/or upgrade) pips in 'pips' make var
pips:
	$(with_venv) pip $(pipargs) install --upgrade $(pips)

#MENU clean:      remove venv & touchfiles
clean:
	if [[ -e $(localdir) ]]; then rm -rf $(localdir); fi
