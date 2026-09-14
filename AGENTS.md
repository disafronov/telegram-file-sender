# AGENTS.md

## Documentation Convention

- **Docstrings**: required on all modules, public functions, and classes.
- **HOW comments**: required when the code takes a non-obvious approach.

## Commands

```sh
make install          # deps + pre-commit hooks
make format           # black + isort
make lint             # black --check, isort --check-only, flake8, mypy, bandit
make test             # pytest with coverage (100% fail_under)
make dead-code        # vulture
make all              # lint -> test -> dead-code
make audit            # pip-audit
make docker-build     # build production image
make docker-run       # run production image (sends the file, then exits)
```

## Lint & Type Check

- **black** (line-length=88), **isort** (profile=black), **flake8** (max-line-length=88, ignores E203/W503)
- **mypy**: strict mode (disallow_untyped_defs, disallow_incomplete_defs, disallow_untyped_decorators, strict_equality). Checks `telegram_file_sender/` only. Excludes: tests/.
- **bandit**: security lint
- **vulture**: dead code detection

Order: `lint` -> `test` -> `dead-code`

## Test Quirks

- Coverage: 100% branch coverage required (`fail_under=100`, `branch=true`)
- Single test: `uv run pytest tests/test_main.py::TestMain::test_success_returns_zero -v`

## Architecture

Single-module CLI: `telegram_file_sender/__main__.py` reads four env vars
(TELEGRAM_BOT_TOKEN, TELEGRAM_FILE_NAME, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_MESSAGE),
posts the file to the Telegram Bot API `sendDocument` endpoint and exits with
0 on success, 1 on any failure.

## Gotchas

- **Env vars**: all four are required; a missing/empty one is a hard error.
- **Exit codes**: exit code is the contract — container/CI run reports success
  only when the file was actually sent. `response.raise_for_status()` turns
  Telegram API errors into non-zero exits.
- **Pre-commit**: runs `make lint` + `uv lock` on commit; `make test` +
  `make dead-code` + `make audit` on push.
- **Conventional commits** enforced via `conventional-pre-commit` hook on
  commit messages.
- **Semantic release**: `main` branch -> stable releases (no prerelease cycle).
- **Docker**: image runs as a non-root `appuser`; the file to send is mounted
  read-only and passed via `TELEGRAM_FILE_NAME`; deps come from `uv.lock`
  (`uv sync --frozen`), dev group is excluded.
