# Development Environment Modernization Specification (Migration to uv)

## Objective

Modernize the project's Python development environment by migrating from the traditional `venv + pip + requirements.txt` workflow to the **uv** ecosystem.

The migration must be completed **without breaking the existing project** or changing application behavior.

The goal is to improve dependency management, reproducibility, installation speed, developer experience, deployment consistency, and future maintainability.

This migration should be transparent to the application itself. Only the development and dependency management workflow should change.

---

# Current Environment

The project currently uses:

```text
Python

↓

py -m venv .venv

↓

pip

↓

requirements.txt
```

This workflow is functional but lacks:

* Reliable dependency locking
* Fast package installation
* Modern dependency management
* Consistent environments across multiple machines

---

# Target Environment

The project should use:

```text
uv

↓

.venv

↓

pyproject.toml

↓

uv.lock
```

The `.venv` directory should still exist.

The difference is that **uv** becomes responsible for creating, synchronizing and managing the virtual environment.

---

# Migration Goals

The migration must:

* Preserve all installed packages.
* Preserve all package versions.
* Preserve compatibility with the existing codebase.
* Preserve Raspberry Pi deployment compatibility.
* Preserve Windows development compatibility.
* Preserve future Linux deployment compatibility.

No application functionality should change.

---

# Dependency Migration

Analyze the current environment.

Collect all installed dependencies.

Generate a proper `pyproject.toml`.

Generate a `uv.lock` file.

Verify that all dependencies are successfully installed through uv.

Do not remove dependencies that are currently required.

---

# Virtual Environment

Replace

```bash
py -m venv .venv
```

with

```bash
uv venv
```

The project should continue using:

```text
.venv/
```

Do not change the virtual environment directory name.

---

# Project Structure

The final project structure should resemble:

```text
project/

.pyproject.toml
uv.lock
.python-version

.venv/

manage.py

apps/
config/
templates/
static/
media/
```

---

# pyproject.toml

Generate a clean and well-structured `pyproject.toml`.

Include:

* Project metadata
* Python version
* Runtime dependencies
* Development dependencies
* Tool configuration

The file should become the single source of truth for dependency management.

---

# Lock File

Generate

```text
uv.lock
```

This file must contain the exact dependency versions required to reproduce the environment on any machine.

---

# Dependency Groups

Separate dependencies into logical groups.

Example:

Runtime

* Django
* Pillow
* mysqlclient
* gunicorn

Development

* pytest
* ruff
* djlint
* ipython

Future

* mypy
* coverage

The project should support installing only runtime dependencies on production systems.

---

# Installation Workflow

The new workflow should become:

Create environment

```bash
uv venv
```

Install all dependencies

```bash
uv sync
```

Install new dependency

```bash
uv add package_name
```

Remove dependency

```bash
uv remove package_name
```

Upgrade dependency

```bash
uv lock --upgrade
```

The old pip workflow should no longer be required.

---

# Development Tools

Evaluate and integrate the following tools where appropriate.

## Ruff

Use Ruff for:

* Linting
* Import sorting
* Formatting (if chosen)

Configure through `pyproject.toml`.

---

## pytest

Ensure the project is compatible with pytest.

Create a basic pytest configuration if one does not already exist.

---

## djLint

Configure djLint for Django templates.

Use it to maintain consistent formatting.

---

## Optional Tools

Evaluate but do not necessarily implement:

* mypy
* coverage
* pre-commit
* tox

Recommend them only if they provide value to the project.

---

# IDE Support

Update project configuration for IDE compatibility.

Ensure proper support for:

* VS Code
* PyCharm

Include:

* Interpreter configuration
* Recommended extensions
* Workspace settings (if appropriate)

---

# Documentation

Update all project documentation.

Update:

README.md

Developer setup instructions

Installation instructions

Deployment instructions

Remove outdated pip commands.

Replace them with uv commands.

---

# Deployment Compatibility

Verify that the project can still be deployed using uv.

The deployment process should work on:

* Windows
* Linux
* Raspberry Pi

Document any required deployment changes.

---

# Git Configuration

Review `.gitignore`.

Ensure it includes:

```text
.venv/
__pycache__/
*.pyc
```

Do not ignore:

```text
uv.lock
pyproject.toml
```

These files should be committed to version control.

---

# Existing Scripts

Review all existing scripts.

Update any scripts that currently rely on:

```bash
pip install

pip freeze

requirements.txt
```

Replace them with the equivalent uv workflow.

---

# Validation

After migration, verify:

* Django starts successfully.
* All installed apps load correctly.
* Database migrations work.
* Static file collection works.
* Management commands function correctly.
* Tests (if present) execute successfully.
* No dependency is missing.

---

# Future Compatibility

The environment should support future additions such as:

* Django REST Framework
* Celery
* Redis
* Channels
* Docker
* GitHub Actions
* Mobile API

without requiring another dependency management migration.

---

# Coding Standards

The migration should:

* Follow Python packaging best practices.
* Avoid unnecessary dependencies.
* Keep configuration clean and organized.
* Use comments where appropriate.
* Avoid modifying unrelated project files.

---

# Deliverables

The migration should produce:

1. `pyproject.toml`
2. `uv.lock`
3. Updated `.gitignore`
4. Updated README
5. Updated developer setup documentation
6. Updated deployment documentation
7. Verified working virtual environment
8. Verified dependency synchronization
9. Optional development tool configuration (Ruff, pytest, djLint)

---

# Acceptance Criteria

The migration will be considered complete when:

* The project installs successfully using `uv sync`.
* The Django application starts without errors.
* All current dependencies are preserved.
* No functionality is broken.
* Development and deployment workflows are simplified.
* Documentation reflects the new workflow.
* Future developers can clone the repository, run `uv sync`, and immediately start working with the project.

The migration should improve the developer experience while remaining fully backward-compatible with the current School ERP codebase.
