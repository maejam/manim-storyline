# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set shell := ["uv", "run", "bash", "-euxo", "pipefail", "-c"]

set positional-arguments

qa *args: format lint type (test args)

@test *args:
    pytest -v "$@"

@lint *args:
    ruff check "$@"

@format *args:
    ruff format "$@"

@type *args:
    mypy "$@"
