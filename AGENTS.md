# AGENTS.md — Expense Tracker

## Project Overview
A Python CLI-based Expense Tracker for managing and analyzing daily expenses. Uses JSON for persistence, OOP design, and Matplotlib for pie chart visualization.

---

## File Structure

| File | Purpose |
|---|---|
| `main.py` | CLI entry point with interactive menu (13 options) |
| `expense.py` | `Expense` data class — title, amount, category, date |
| `expense_manager.py` | `ExpenseManager` class — all business logic & I/O |
| `data.json` | Persistent expense storage (12 sample entries) |
| `requirements.txt` | Dependency: `matplotlib` |
| `README.md` | Project docs with screenshots |
| `screenshots/` | 6 PNG screenshots of the CLI and charts |
| `Token_for_Git.txt` | **⚠️ Contains leaked GitHub PAT — needs immediate removal** |
| `.gitignore` | Ignores `__pycache__/` and `*.pyc` |

---

## Core Classes

### `Expense` (`expense.py:3`)
- **Fields:** `title`, `expense_amount`, `category`, `_created_at`
- **Key methods:** `get_title()`, `get_amount()`, `get_date()`, `get_category()`, `__str__()`, `to_dict()`
- Date format: `"%Y-%m-%d %H:%M:%S"`

### `ExpenseManager` (`expense_manager.py:15`)
- Manages a list of `Expense` objects
- Persists to/from `data.json` via `save_expenses()` / `load_expenses()`
- **Static helper:** `detect_category(title)` — keyword-based auto-categorization
- Categories: Food, Travel, Entertainment, Shopping (with keyword lists)
- Default category: "Others"

---

## CLI Features (main.py)

| # | Feature | Method |
|---|---|---|
| 1 | Add Expense | `add_expense()` |
| 2 | View Expenses | `view_expenses()` |
| 3 | Total Expenses | `show_total()` |
| 4 | Category-wise Report | `category_wise_expenses()` |
| 5 | Date-wise Report | `date_wise_expenses()` |
| 6 | Delete Expense | `delete_expense()` |
| 7 | Monthly Report | `monthly_expenses()` |
| 8 | Search Expense | `search_expense(keyword)` |
| 9 | Edit Expense | `edit_expense()` |
| 10 | Top Spending Category | `top_spending_category()` |
| 11 | Pie Chart | `pie_chart_visualization()` |
| 12 | CSV Export | `export_csv_report()` |
| 13 | Exit | — |

---

## Current Data (`data.json`)
- 12 expense entries spanning **May–August 2026**
- Categories: Food (5), Travel (4), Entertainment (2)
- Total stored amount: ~10,150.00

---

## Known Issues / Bugs

1. **Monthly report bug** (`expense_manager.py:133`): `monthly_expenses()` uses `month_name` as the dict key in `get()` instead of `month_year`. This causes months to collapse incorrectly across years (e.g., May 2025 and May 2026 would merge).

2. **Pie chart save order** (`expense_manager.py:241`): `plt.show()` blocks execution, so `plt.savefig()` on line 243 only runs after the chart window is closed. Swap the order for reliable saving.

3. **Excess trailing blank lines** (`expense_manager.py:245-300`): File has ~55 blank lines at the end.

4. **No tests** — zero test files exist.

---

## Security Issues

- **`Token_for_Git.txt`** contains a GitHub personal access token (`ghp_...`). This file is currently untracked but should be:
  1. Revoked immediately on GitHub
  2. Deleted from disk
  3. Added to `.gitignore`

---

## Git State

- **Branch:** `main` (up to date with `origin/main`)
- **Commits:** 1 (`7cd2e29` — "Initial commit")
- **Unstaged changes:** `data.json` modified
- **Untracked:** `Token_for_Git.txt`

---

## Dependencies

- `matplotlib` (for pie chart)

---

## Code Style Notes
- Uses getter methods (`get_title()`, `get_amount()`, etc.) but also accesses attributes directly (e.g., `expense.title` in `edit_expense()`)
- Inconsistent spacing around operators and colons
- `pie_chart_visualization()` uses late import for `matplotlib.pyplot`
- No type hints anywhere in the codebase
- `Expense` constructor default category is `'others'` (lowercase), but `detect_category` returns `"Others"` (capitalized)
