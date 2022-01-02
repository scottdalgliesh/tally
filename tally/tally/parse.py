import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from tika import parser


@dataclass
class Transaction:
    """Class for transaction data extracted from a banking statement."""

    Date: date
    Description: str
    Value: float
    Category: Optional[str] = None


TransactionSet = list[Transaction]


def _parse_text(path_to_file: str | Path) -> str:
    """Parse statement text from pdf."""
    return parser.from_file(str(path_to_file))["content"]  # type: ignore


def _get_statement_dates(statement_text: str) -> tuple[date, date]:
    """Parse the statement start and end date from the statement text."""
    pattern = re.compile(r"STATEMENT FROM (\D{3} \d{2}(, \d{4})?) TO (\D{3} \d{2}, \d{4})")
    match = re.search(pattern, statement_text)
    if match is None:
        raise ValueError("Error parsing statement beginning and end dates.")
    end_date = datetime.strptime(match.group(3), "%b %d, %Y").date()

    # add start date year (identical to end date year if omitted in statement)
    if match.group(2) is None:
        start_text = f"{match.group(1)}, {str(end_date.year)}"
    else:
        start_text = match.group(1)
    start_date = datetime.strptime(start_text, "%b %d, %Y").date()
    return start_date, end_date


def _get_transactions(statement_text: str, start_date: date, end_date: date) -> TransactionSet:
    """Parse the transactions from the statement text."""
    pattern = re.compile(r"(\D{3} \d{2}) \D{3} \d{2} (.+)\n+\d+\n+(-?\$\d+\.\d+)")
    matches = list(re.finditer(pattern, statement_text))
    if len(matches) == 0:
        raise ValueError("No transactions matched while parsing the statement.")

    transaction_set = []
    for match in matches:
        # extract transaction date, description & value from regex match
        date_str = match.group(1)
        description = match.group(2)
        value = float(match.group(3).replace("$", ""))

        # add year to date string and convert to date object
        if date_str.split()[0] == start_date.strftime("%b").upper():
            date_str = f"{date_str} {start_date.year}"
        else:
            date_str = f"{date_str} {end_date.year}"
        date_obj = datetime.strptime(date_str, "%b %d %Y").date()

        trans = Transaction(Date=date_obj, Description=description, Value=value)
        transaction_set.append(trans)

    return transaction_set


def parse_statement(path_to_file: str | Path) -> TransactionSet:
    """Parse transactions from pdf statement."""
    statement_text = _parse_text(path_to_file=path_to_file)
    start_date, end_date = _get_statement_dates(statement_text=statement_text)
    return _get_transactions(
        statement_text=statement_text,
        start_date=start_date,
        end_date=end_date,
    )
