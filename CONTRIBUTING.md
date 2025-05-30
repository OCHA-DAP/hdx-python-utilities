# Development

## Environment

Development is currently done using Python 3.12. We recommend using a virtual
environment such as ``venv``:

    python3.12 -m venv venv
    source venv/bin/activate

In your virtual environment, please install all packages for
development by running:

    pip install -r requirements.txt

## Pre-Commit

Also be sure to install `pre-commit`, which is run every time
you make a git commit:

    pre-commit install

With pre-commit, all code is formatted according to
[ruff](https://docs.astral.sh/ruff/) guidelines.

To check if your changes pass pre-commit without committing, run:

    pre-commit run --all-files

## Testing

To run the tests and view coverage, execute:

    pytest --cov hdx

Follow the example set out already in ``documentation/main.md`` as you write the documentation.

## Packages

[uv](https://github.com/astral-sh/uv) is used for
package management.  If you’ve introduced a new package to the
source code (i.e.anywhere in `src/`), please add it to the
`project.dependencies` section of
`pyproject.toml` with any known version constraints.

To add packages for testing or development, add them to the `test` or `dev`
sections under `[project.optional-dependencies]`.

Any changes to the dependencies will be automatically reflected in
`requirements.txt` with `pre-commit`, but you can re-generate
the file without committing by executing:

    pre-commit run pip-compile --all-files

## Project

[Hatch](https://hatch.pypa.io/) is used for project management. The project
can be built using:

    hatch build

Linting and syntax checking can be run with:

    hatch fmt --check

Tests can be executed using:

    hatch test
