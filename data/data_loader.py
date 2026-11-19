"""CSV/XLSX readers that keep Pandas out of the active app import path."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from typing import Any
import zipfile

from openpyxl import load_workbook

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_WORKBOOK_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_WORKBOOK_ENTRIES = 1000


def _validate_content_size(content: bytes) -> None:
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("The uploaded file exceeds the 20 MiB size limit.")


def _validate_workbook_archive(content: bytes) -> None:
    with zipfile.ZipFile(BytesIO(content)) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_WORKBOOK_ENTRIES:
            raise ValueError("The workbook contains too many internal files.")
        if sum(entry.file_size for entry in entries) > MAX_WORKBOOK_UNCOMPRESSED_BYTES:
            raise ValueError("The workbook expands beyond the 100 MiB processing limit.")


def excel_sheet_names(filename: str, content: bytes) -> list[str]:
    """Return worksheet names from an uploaded XLSX file."""
    _validate_content_size(content)
    if not filename.lower().endswith(".xlsx"):
        raise ValueError("Worksheet selection is available for .xlsx files.")
    _validate_workbook_archive(content)
    workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        return list(workbook.sheetnames)
    finally:
        workbook.close()


def parse_uploaded_file(
    filename: str,
    content: bytes,
    sheet_name: str | None = None,
) -> tuple[list[str], list[list[Any]]]:
    """Read CSV or one explicitly selected XLSX sheet into column and row lists."""
    _validate_content_size(content)
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        parsed = list(csv.reader(StringIO(content.decode("utf-8-sig"))))
    elif lower_name.endswith(".xlsx"):
        _validate_workbook_archive(content)
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
        try:
            if sheet_name is None:
                if len(workbook.sheetnames) != 1:
                    raise ValueError("Choose an Excel worksheet before loading the data.")
                sheet_name = workbook.sheetnames[0]
            if sheet_name not in workbook.sheetnames:
                raise ValueError(f"Worksheet {sheet_name!r} is not present in the workbook.")
            worksheet = workbook[sheet_name]
            parsed = [list(row) for row in worksheet.iter_rows(values_only=True)]
        finally:
            workbook.close()
    else:
        raise ValueError("Supported upload formats are .csv and .xlsx.")
    if not parsed:
        raise ValueError("The uploaded file contains no rows.")
    headers = [str(value) if value is not None else f"Column {index + 1}"
               for index, value in enumerate(parsed[0])]
    seen_headers: dict[str, int] = {}
    for index, header in enumerate(headers):
        seen_headers[header] = seen_headers.get(header, 0) + 1
        if seen_headers[header] > 1:
            headers[index] = f"{header} ({seen_headers[header]})"
    rows = [row + [None] * (len(headers) - len(row)) for row in parsed[1:]]
    return headers, [row[:len(headers)] for row in rows]


def load_file(uploaded_file, sheet_name: str | None = None):
    """Compatibility wrapper returning a DataFrame for legacy callers."""
    columns, rows = parse_uploaded_file(
        uploaded_file.name, uploaded_file.getvalue(), sheet_name=sheet_name,
    )
    import pandas as pd

    return pd.DataFrame(rows, columns=columns)
