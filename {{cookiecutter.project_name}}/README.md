# {{ cookiecutter.friendly_name }}

## Setup

1. Open a terminal session to this project directory
2. `poetry shell`; make sure the venv is created woth correct python
3. `poetry install`
4. `code .`
   - You may have to select the python interpreter, use `./.venv/bin/python`
   - You can choose to use the repo in a devcontainer if you want. It has some vscode settings and extensions preconfigured.
5. Setup git
   1. Create a git repo
   2. `pre-commit install`
6. Rename `.env.sample` to `.env` and fill in the Preset password

