# {{ cookiecutter.friendly_name }}

## Setup

1. In OS Terminal cd to project directory
2. `poetry install`; make sure the venv is created woth correct python
3. `code .`
   - You may have to select the python interpreter, use `./.venv/bin/python`
   - You can choose to use the repo in a devcontainer if you want. It has some vscode settings and extensions preconfigured.
4. Setup git
   1. Create a git repo
   2. `pre-commit install`
5. Rename `.env.sample` to `.env` and fill in the Preset password

