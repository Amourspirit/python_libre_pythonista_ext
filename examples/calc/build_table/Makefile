help:
	@echo "Run make build to compile into 'build/buld_table' folder."
	@echo "Run make macro to compile into 'macro/builder.py' file."
	@echo "Run make tbl to open calc and create table"
	@echo "Run make tbl-style to open calc and create table with style"
	@echo "Run make tbl-chart to open calc and create table with style and chart"

.PHONY: build macro help tbl tbl-style tbl-chart

build:
	oooscript compile --embed --config "$(PWD)/config.json" --embed-doc "$(PWD)/builder.ods" --build-dir "build/buld_table"

macro:
	oooscript compile --config "$(PWD)/config.json" --build-dir "macro"

tbl:
	python $(PWD)/run.py

tbl-style:
	python $(PWD)/run.py "style"

tbl-chart:
	python $(PWD)/run.py "chart"