#!/bin/make

########### CONFIGURATION ########################
PROJECT="cnfgen"
REMOTE="massimo@massimolauria.net:/srv/www/massimolauria.net/cnfgen/"
SOURCES=index.org benchmarks.org transformation.org background.org graphformats.org
EMACS=emacs



ifeq ($(shell uname -s),Darwin)
BROWSE=open
EMACS=/Applications/Emacs.app/Contents/MacOS/Emacs
else
BROWSE=xdg-open
endif


########### THE RULES ############################

TARGET= $(SOURCES:.org=.html)

all: version ${TARGET}

version:
	@$(EMACS) -Q -batch -l setup.el -f version-report >/dev/null

clean:
	@-rm -rf ltxpng/
	@-rm -f  ${TARGET}

view: ${TARGET}
	@${BROWSE} index.html

%.html: %.org
	@$(EMACS) -Q -batch --visit=$< -l setup.el -f export-org-file >/dev/null

deploy: all
	rsync -rvz --chmod='u=rwX,go=rX' . $(REMOTE)

.PHONY: all clean view version deploy
