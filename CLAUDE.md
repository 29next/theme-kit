# Next Commerce Theme Kit

CLI tool (`ntk`) for building and maintaining storefront themes on the Next Commerce platform. Supports Sass processing via `libsass`.

## Project Structure

```
ntk/
  __main__.py    # Entry point
  command.py     # All CLI commands (watch, push, pull, checkout, init, list, sass)
  conf.py        # Config loading and constants
  decorator.py   # @parser_config decorator for command validation
  gateway.py     # API client for Next Commerce store
  utils.py       # Helpers (get_template_name, progress_bar)
tests/
  test_command.py
  test_gateway.py
  test_config.py
  test_installer.py
```

## Development Setup

### Prerequisites

- Python 3.10 or higher — check with `python --version`
- `pip` — usually included with Python
- On macOS, Python can be installed via [Homebrew](https://brew.sh): `brew install python`
- On Windows, use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) (recommended) or the [Windows App Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5)

### First-time Setup

```bash
# Clone the repo
git clone https://github.com/29next/theme-kit.git
cd theme-kit

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install the package with test dependencies
pip install -e ".[test]"
```

### Installing the CLI Globally (for end users)

```bash
pip install next-theme-kit

# Or with pipx (recommended — keeps it isolated)
pipx install next-theme-kit
```

## Running Tests

```bash
pytest tests/ -v
pytest --cov=ntk --cov-report xml
```

## Key Dependencies

- `watchfiles` — file watching for `ntk watch` (replaced deprecated `watchgod`)
- `libsass` — Sass/SCSS processing
- `PyYAML` — config.yml parsing
- `requests` — HTTP client for store API

## Python Support

Requires Python >= 3.10. Tested against 3.10, 3.11, 3.12, 3.13, 3.14 via tox and GitHub Actions.

## Important Conventions

- Use `asyncio.run()` for async entry points — not `get_event_loop()` (broke in Python 3.12+)
- `watchfiles.Change` is an `IntEnum` — use `event_type.name.title()` for human-readable log output, not `str(event_type)`
- `watchfiles` internal logging is suppressed via `logging.getLogger('watchfiles').setLevel(logging.WARNING)`
- Test dependencies are declared as `extras_require={"test": ...}` in `setup.py`
