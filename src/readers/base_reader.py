"""Base reader utilities for CSV parsing and normalization.

`BaseReader` provides a reusable `_read_rows` helper that validates headers
and normalizes CSV rows into dictionaries for downstream models.
"""

import csv
from abc import ABC, abstractmethod
from pathlib import Path


class BaseReader(ABC):
    """Abstract base class for CSV readers."""

    @abstractmethod
    def read(self, filepath: str) -> list:
        """Read rows from a CSV file.

        Args:
            filepath (str): Path to the CSV file.

        Returns:
            list: Parsed rows.

        Raises:
            FileNotFoundError: When the file does not exist.
            ValueError: When required headers are missing.
        """
        raise NotImplementedError("Subclasses must implement read().")

    def _read_rows(self, filepath: str, expected_fields: list[str]) -> list[dict[str, str]]:
        """Read and normalize rows with the expected fields.

        Args:
            filepath (str): Path to the CSV file.
            expected_fields (list[str]): Required CSV columns.

        Returns:
            list[dict[str, str]]: Normalized raw rows.

        Raises:
            FileNotFoundError: When the file does not exist.
            ValueError: When headers are missing or malformed.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        with path.open("r", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV file is missing a header row.")
            missing = [field for field in expected_fields if field not in reader.fieldnames]
            if missing:
                missing_list = ", ".join(missing)
                raise ValueError(f"Missing required columns: {missing_list}")
            rows: list[dict[str, str]] = []
            for row in reader:
                rows.append({field: (row.get(field) or "").strip() for field in expected_fields})
        return rows
