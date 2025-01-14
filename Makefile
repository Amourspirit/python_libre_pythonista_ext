help:
	@echo "Run make build to compile into 'build' folder and create dist"
	@echo "Run make build to compile into 'build' folder without creating dist"
	@echo "Run make build_idl to compile idl"
	@echo "Run make diff to write 'changes_since_last_commit.diff into' into 'tmp' folder."
	@echo "Run make diff_sum to write 'summary_since_last_commit.diff into' into 'tmp' folder."

.PHONY: build build_idl build_no_dist diff diff_sum help

build:
	uv run --no-config make.py build --no-idl

build_no_dist:
	uv run --no-config make.py build --no-idl --no-dist

build_idl:
	uv run --no-config make.py build

create_build_dir:
	mkdir -p tmp

diff: create_build_dir
	git diff HEAD > ./tmp/changes_since_last_commit.diff

diff_sum: create_build_dir
	git diff HEAD --compact-summary > ./tmp/summary_since_last_commit.diff