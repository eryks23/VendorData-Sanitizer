# VendorData-Sanitizer

> Lightweight Python utility for validating, classifying, and auditing vendor records — no external dependencies required.

## Description

VendorData-Sanitizer processes raw vendor data by validating VAT identifiers and email addresses, classifying each record as `DOMESTIC` or `INTERNATIONAL`, and writing the results to separate CSV files. It targets finance, procurement, and data-operations teams that need a quick, dependency-free way to catch bad records before they enter a master data system.

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage / Quick Start](#usage--quick-start)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## Key Features

- **Country-aware VAT validation** — full 12-character PL-prefix rule enforced for Polish vendors; minimum-length guard for all other countries.
- **Email validation** — presence of `@` and `.` checked for every record before it is accepted.
- **Automatic vendor classification** — each record is tagged `DOMESTIC` (country `PL`) or `INTERNATIONAL` at processing time.
- **Split CSV output** — valid records are written to `audit_correct.csv`; invalid records go to `audit_errors.csv` with a human-readable `error_reason` column explaining every failure.
- **Zero external dependencies** — relies solely on the Python standard library (`csv` module).

## Tech Stack

| Layer        | Technology     |
|--------------|----------------|
| Language     | Python 3.8+    |
| I/O          | `csv` (stdlib) |
| Dependencies | None           |

## Requirements

- Python 3.8 or newer
- No third-party packages required

## Installation

```bash
# Clone the repository
git clone https://github.com/eryks23/VendorData-Sanitizer.git
cd VendorData-Sanitizer
```

No virtual environment or `pip install` step is necessary — the project uses only the Python standard library.

## Usage / Quick Start

Run the script directly from the project root:

```bash
python vendor_audit.py
```

Expected console output:

```
Starting data audit...
Total processed: 4
Valid: 2 | Faulty: 2
Successfully saved 2 records to: audit_errors.csv
Successfully saved 2 records to: audit_correct.csv
```

Two CSV files are written to the working directory:

**`audit_correct.csv`** — records that passed all validations:

```csv
id,name,vat_id,email,country,group
1001,Tech Corp,PL1234567890,contact@tech.pl,PL,DOMESTIC
1004,Berlin Bau,DE987654321,info@berlin.de,DE,INTERNATIONAL
```

**`audit_errors.csv`** — records that failed at least one check, with an `error_reason` column:

```csv
id,name,vat_id,email,country,group,error_reason
1002,Global Soft,123,bad_mail.com,US,INTERNATIONAL,"VAT valid: False, Email valid: False"
1003,Local Biz,PL0987654321,,PL,DOMESTIC,"VAT valid: True, Email valid: False"
```

> **Note:** Input data is currently hardcoded in the `main()` function inside `vendor_audit.py`. To process your own records, replace the `raw_data` list in `main()` with your data or extend `main()` to read from an external CSV file.

## API Documentation

### `validate_vat(vat_id: str, country: str) -> bool`

Validates a VAT identifier against country-specific rules.

| Parameter | Type  | Description                                            |
|-----------|-------|--------------------------------------------------------|
| `vat_id`  | `str` | The VAT identifier to validate                         |
| `country` | `str` | ISO 3166-1 alpha-2 country code (e.g. `"PL"`, `"DE"`) |

**Returns:** `True` if the identifier is valid for the given country, `False` otherwise.

**Validation rules:**

| Country | Rule                                           |
|---------|------------------------------------------------|
| `PL`    | Exactly 12 characters, must start with `"PL"` |
| Other   | Length must be greater than 3 characters       |
| Any     | Empty string always returns `False`            |

```python
validate_vat("PL1234567890", "PL")  # True
validate_vat("PL123", "PL")         # False — wrong length
validate_vat("123", "US")           # False — too short
validate_vat("", "DE")              # False — empty
```

---

### `validate_email(email: str) -> bool`

Checks whether an email address contains the minimum required characters.

| Parameter | Type  | Description                   |
|-----------|-------|-------------------------------|
| `email`   | `str` | The email address to validate |

**Returns:** `True` if both `"@"` and `"."` are present in the string, `False` otherwise.

```python
validate_email("user@example.com")  # True
validate_email("bad_mail.com")      # False — missing @
validate_email("no-dot@domain")     # False — missing .
validate_email("")                  # False — empty
```

---

### `process_data(vendors: list[dict]) -> tuple[list[dict], list[dict]]`

Iterates over a list of vendor dictionaries, validates each record, and splits the results into two lists.

| Parameter | Type         | Description                                                                      |
|-----------|--------------|----------------------------------------------------------------------------------|
| `vendors` | `list[dict]` | List of vendor records; each dict must contain `vat_id`, `email`, and `country`  |

**Returns:** A tuple `(valid_records, error_records)`:

- `valid_records` — records that passed both validations; each dict gains a `group` key (`"DOMESTIC"` or `"INTERNATIONAL"`).
- `error_records` — records that failed at least one check; each dict gains `group` and `error_reason` keys.

```python
vendors = [
    {"id": 1, "name": "Acme",     "vat_id": "PL1234567890", "email": "a@b.pl",    "country": "PL"},
    {"id": 2, "name": "Bad Corp", "vat_id": "X",            "email": "notanemail", "country": "US"},
]

valid, errors = process_data(vendors)
# valid  → [{"id": 1, ..., "group": "DOMESTIC"}]
# errors → [{"id": 2, ..., "group": "INTERNATIONAL",
#             "error_reason": "VAT valid: False, Email valid: False"}]
```

---

### `save_results(data: list[dict], filename: str) -> None`

Writes a list of vendor records to a UTF-8 encoded CSV file using all keys present in the first record as column headers.

| Parameter  | Type         | Description                                          |
|------------|--------------|------------------------------------------------------|
| `data`     | `list[dict]` | Records to write; all dicts must share the same keys |
| `filename` | `str`        | Output file path (relative or absolute)              |

Prints a confirmation message including the record count on success. If `data` is empty, logs a warning and returns without creating the file.

```python
save_results(valid_records, "audit_correct.csv")
# → Successfully saved 2 records to: audit_correct.csv
```

---

### `main() -> None`

Script entry point. Defines the `raw_data` list, calls `process_data()`, and writes both result files via `save_results()`. Modify `raw_data` to change the input dataset.

## Project Structure

```
VendorData-Sanitizer/
├── vendor_audit.py      # Core script — validation logic and entry point
├── audit_correct.csv    # Sample output: records that passed validation
├── audit_errors.csv     # Sample output: records that failed validation
├── requirements.txt     # Dependency manifest (stdlib only — no packages to install)
├── LICENSE              # MIT License
└── README.md            # Project documentation
```

## Testing

No automated test suite exists yet. To verify behaviour manually, modify the `raw_data` list in `main()` and run the script:

```bash
python vendor_audit.py
```

To add automated tests, create a `tests/` directory and use `pytest`:

```bash
pip install pytest
pytest tests/
```

Example test structure:

```python
# tests/test_validators.py
from vendor_audit import validate_vat, validate_email, process_data

def test_vat_valid_pl():
    assert validate_vat("PL1234567890", "PL") is True

def test_vat_invalid_pl_short():
    assert validate_vat("PL123", "PL") is False

def test_email_valid():
    assert validate_email("user@example.com") is True

def test_email_missing_at():
    assert validate_email("bad_mail.com") is False

def test_process_data_splits_correctly():
    vendors = [
        {"id": 1, "name": "OK",  "vat_id": "PL1234567890", "email": "a@b.pl", "country": "PL"},
        {"id": 2, "name": "Bad", "vat_id": "X",            "email": "no",      "country": "US"},
    ]
    valid, errors = process_data(vendors)
    assert len(valid) == 1
    assert len(errors) == 1
    assert valid[0]["group"] == "DOMESTIC"
    assert "error_reason" in errors[0]
```

## Roadmap

- [ ] Accept input from an external CSV file via a command-line argument instead of hardcoded `raw_data`
- [ ] Implement full EU VAT format validation for additional country codes (DE, FR, GB, CZ, etc.)
- [ ] Strengthen email validation with a regex pattern or the `email-validator` library
- [ ] Add a `--dry-run` flag to preview results without writing output files
- [ ] Write a `pytest` test suite covering edge cases for all validator functions
- [ ] Package as a proper CLI tool using `argparse`

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`
3. Commit with a clear message: `git commit -m "feat: describe what changed"`
4. Push to your fork: `git push origin feature/my-change`
5. Open a Pull Request against `main`.

Keep functions small and focused on a single responsibility. New validation rules should follow the pattern established by `validate_vat()` and `validate_email()`.

## Author

Github: [@eryks23](https://github.com/eryks23)

Repository: [https://github.com/eryks23/VendorData-Sanitizer](https://github.com/eryks23/VendorData-Sanitizer)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.
