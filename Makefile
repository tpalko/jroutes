SHELL=/bin/bash
#export CHANGES = `git status -s -- src/jroutes | wc -l`
CHANGES = $(shell git status -s -- src/jroutes | wc -l)

test:
	gunicorn -b 0.0.0.0:9000 jroutes.serving:handler

version:
ifeq ($(CHANGES), 0)
	standard-version --dry-run
else
	@echo "No versioning today ($(CHANGES) changes)"
endif

build:
	python3 -m build 

release: build 
	python3 -m twine upload --repository testpypi dist/*

clean:
	rm -rf dist 
	rm -rf src/*.egg-info
