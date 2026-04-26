# Contributing to Nikolai 0.3

Nikolai is a high-availability project with strict architectural locking.

## 1. Development Principles
- **Async First:** All new components must be asynchronous and non-blocking.
- **Layered Responsibility:** Keep reflexes in `brain/silica` and reasoning in `brain/core`.
- **Contract Enforcement:** All module interactions must be defined in a `module_contract.json`.

## 2. Code Standards
- Use Type Hints for all Python code.
- Ensure every new subdirectory has an `__init__.py` file.
- Update the system version using `build_scripts/version_stamp.ps1` after every architectural change.

## 3. Pull Request Process
1. Update relevant documentation in `Docs/`.
2. Synchronize the `project_spine.json`.
3. Verify the build using the `codebase_investigator` agent.
