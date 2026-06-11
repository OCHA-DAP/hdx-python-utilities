# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**hdx-python-utilities** is a general-purpose Python utility library (not HDX-specific) providing helpers for: downloading files, retrieving tabular data (CSV/JSON/XLSX), date parsing, JSON/YAML I/O, dict/list manipulation, HTML parsing, file hashing, text processing, error handling, and more.

## Commands

```bash
# Install dependencies
uv sync

# Run all tests with coverage
uv run pytest

# Run a single test file
uv run pytest tests/hdx/utilities/test_downloader.py

# Run a single test by name
uv run pytest tests/hdx/utilities/test_downloader.py -k "test_download_file"

# Lint and format
uv run ruff check
pre-commit run --all-files

# Build
uv build
```

Coverage is written to `coverage.lcov` and JUnit XML to `test-results.xml`.

## Source Layout

All source lives under `src/hdx/utilities/`. Tests mirror the layout under `tests/hdx/utilities/` with fixtures in `tests/fixtures/`.

Key modules:
- `base_downloader.py` — `BaseDownload` ABC defining the interface (`download_file`, `download_tabular_rows`, etc.) and `DownloadError`
- `downloader.py` — `Download(BaseDownload)`: HTTP downloading via `requests` + `frictionless` for tabular parsing; supports auth (basic, bearer, extra params), rate limiting, retries, and streaming rows
- `retriever.py` — `Retrieve(BaseDownload)`: wraps a `Download`, adding save/load-from-disk and static fallback directories; registered instances in `Retrieve.retrievers` dict
- `session.py` — `get_session()` builds a `requests.Session` with retry logic and auth headers
- `frictionless_wrapper.py` — thin wrapper around `frictionless.TableResource` for tabular reads
- `loader.py` / `saver.py` — JSON and YAML I/O (YAML uses `ruamel.yaml` to preserve order/comments)
- `dateparse.py` — date/time parsing and timezone utilities
- `dictandlist.py` — dict/list helpers (merge, flatten, key renaming, etc.)
- `path.py` — `script_dir()`, temp dir helpers, `NotFoundError`
- `error_handler.py` / `errors_onexit.py` — structured error accumulation and on-exit reporting
- `text.py` — text processing including `smart_split`
- `matching.py` — fuzzy/phonetic matching utilities
- `state.py` — lightweight on-disk state persistence
- `useragent.py` — user-agent string construction (reads `~/.useragent.yaml` by default)

## Key Patterns

**Download / Retrieve layering** — `Download` handles raw HTTP; `Retrieve` adds a save/use_saved/fallback layer on top. Callers typically use `Retrieve` rather than `Download` directly. Both implement `BaseDownload` so they're interchangeable.

**Tabular row iteration** — `download_tabular_rows()` (on both `Download` and `Retrieve`) yields dicts via `frictionless.TableResource`. The `frictionless_wrapper.py` module handles the `FrictionlessException` boundary. Supports CSV, JSON, XLSX, and XLS.

**User-agent requirement** — `Download` requires a user agent. Either set a global user agent via `UserAgent.set_global(...)` or pass `user_agent=` directly. Missing user agent raises at construction time.

**Context manager usage** — `Download` and `Retrieve` are designed as context managers (`with Download(...) as downloader:`). `__exit__` closes the session.

**Auth precedence** — environment variables `EXTRA_PARAMS`, `BASIC_AUTH`, `BEARER_TOKEN` override constructor arguments. Among constructor args: `auth` > `basic_auth`/`basic_auth_file` > `bearer_token`/`bearer_token_file` > `extra_params_dict` > `extra_params_json`/`extra_params_yaml`.

## Code Style

- Python ≥ 3.10; type hints throughout using `X | Y` union syntax (PEP 604)
- Google-style docstrings with `Args:` and `Returns:` sections
- Formatted and linted with `ruff` (rules: E, F, I, UP; E501 ignored)
- No inline comments unless the *why* is non-obvious

## Collaboration Style

- Be objective, not agreeable. Push back when you disagree, flag tradeoffs honestly.
- Keep explanations brief and to the point.
- Don't rely on recalled knowledge for facts that could be stale. Read the actual source first.

## Scope of Changes

When fixing a bug or addressing PR feedback, change only what is necessary to resolve the specific issue. Do not refactor surrounding code, rename variables, adjust formatting, or make improvements in the same commit unless they are directly required by the fix.
