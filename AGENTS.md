# Repository Guidelines

This project uses both Python and JavaScript/TypeScript. Keep the codebase clean and organized so that continuous integration (CI) runs smoothly.

## Directory layout

- `src/` contains Python source modules.
- `tests/` holds Python test suites executed with **pytest**.
- `js/` contains JavaScript/TypeScript sources. Tests for this code live in `js/__tests__/` and run with **jest**.
- Miscellaneous project documentation and configuration live in the repository root.

## Style

- Format Python code with **Black** and lint with **Ruff**.
- Format JavaScript/TypeScript with **Prettier**.
- Python files use 4 spaces per indent. JavaScript/TypeScript uses 2 spaces.

## Running tests

- Execute `pytest` from the repository root to run the Python test suite.
- Execute `npm test` in the `js/` directory to run the jest suite.

## CI expectations

Pull requests should pass all linting and test commands:

```bash
ruff .
black --check .
prettier --check "js/**/*.{js,ts}"
pytest
( cd js && npm test )
```

CI will fail if any of these steps fail. Ensure new code includes appropriate tests.

## Coding conventions

- Keep commit messages concise yet descriptive.
- Provide docstrings for all public Python classes and functions.
- Use type hints in new Python code where practical.
- Prefer descriptive variable names and avoid large functions; break complex logic into smaller helpers.
