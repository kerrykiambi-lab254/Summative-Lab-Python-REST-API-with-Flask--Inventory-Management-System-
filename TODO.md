# TODO - CLI interactive menu + tests

- [x] Update `inventory_system/cli.py` to display an interactive selection menu (via `input()`) when no subcommand is provided.

- [x] Wire selected option to existing CLI functions (list/view/add/update/delete/search).

- [x] Update `tests/test_cli.py` to mock `input()` and `sys.argv` so the menu path is exercised.

- [x] Add/adjust assertions so tests verify menu-triggered behavior (e.g., banner + list output).

- [x] Run `pytest` and ensure the full suite passes.


