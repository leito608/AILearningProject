# Langc-course

## Setup

Install the project dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

To add a package dependency, run:

```bash
uv add <package-name>
```

This adds the dependency to `pyproject.toml` and updates `uv.lock`.

## Run

```bash
uv run main.py
```