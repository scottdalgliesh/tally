# pylint: disable=[missing-function-docstring, missing-class-docstring]
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pytest

from tally.tally.parse import (
    Transaction,
    TransactionSet,
    _get_statement_dates,
    _get_transactions,
    parse_statement,
)


@dataclass
class SampleStatement:
    path_to_file: str | Path
    statement_text: str = field(init=False)
    start_date: date
    end_date: date
    transactions: TransactionSet

    def __post_init__(self):
        with open(self.path_to_file, encoding="utf8") as file:
            self.statement_text = file.read()


sample_statement_1 = SampleStatement(
    path_to_file="tests/tally/data/sample_statement_text1.txt",
    start_date=date(2019, 3, 20),
    end_date=date(2019, 4, 22),
    transactions=[
        Transaction(date(2019, 3, 22), "TIM HORTONS TORONTO ON", 44.71),
        Transaction(date(2019, 3, 23), "PETROCAN TORONTO ON", 16.27),
        Transaction(date(2019, 4, 1), "PAYMENT - THANK YOU / PAIEMENT - MERCI", -143.66),
        Transaction(date(2019, 3, 23), "CANADIAN TIRE TORONTO ON", 28.56),
        Transaction(date(2019, 3, 27), "REN'S PET DEPOT TORONTO ON", 34.94),
        Transaction(date(2019, 4, 10), "GREASY PIZZA PLACE TORONTO ON", 25.03),
        Transaction(date(2019, 4, 12), "SHELL TORONTO ON", 43.79),
    ],
)

sample_statement_2 = SampleStatement(
    path_to_file="tests/tally/data/sample_statement_text2.txt",
    start_date=date(2019, 12, 20),
    end_date=date(2020, 1, 20),
    transactions=[
        Transaction(date(2019, 12, 20), "TIM HORTONS TORONTO ON", 44.71),
        Transaction(date(2019, 12, 23), "PETROCAN TORONTO ON", 16.27),
        Transaction(date(2020, 1, 1), "PAYMENT - THANK YOU / PAIEMENT - MERCI", -143.66),
        Transaction(date(2019, 12, 28), "CANADIAN TIRE TORONTO ON", 28.56),
        Transaction(date(2020, 1, 5), "REN'S PET DEPOT TORONTO ON", 34.94),
        Transaction(date(2020, 1, 6), "GREASY PIZZA PLACE TORONTO ON", 25.03),
        Transaction(date(2020, 1, 10), "SHELL TORONTO ON", 43.79),
    ],
)


test_input = [
    pytest.param(sample_statement_1, id="mid-year"),
    pytest.param(sample_statement_2, id="end-of-year-transition"),
]


@pytest.mark.parametrize("sample", test_input)
def test_get_statement_dates(sample: SampleStatement):
    start_date, end_date = _get_statement_dates(sample.statement_text)
    assert start_date == sample.start_date
    assert end_date == sample.end_date


@pytest.mark.parametrize("sample", test_input)
def test_get_transactions(sample: SampleStatement):
    transactions = _get_transactions(sample.statement_text, sample.start_date, sample.end_date)
    assert transactions == sample.transactions


@pytest.mark.parametrize(
    "mock_tika, sample",
    [
        pytest.param(sample_statement_1.statement_text, sample_statement_1, id="mid-year"),
        pytest.param(
            sample_statement_2.statement_text, sample_statement_2, id="end-of-year-transition"
        ),
    ],
    indirect=["mock_tika"],
)
def test_parse_statement(mock_tika, sample: SampleStatement):  # pylint: disable=unused-argument
    transactions = parse_statement(sample.path_to_file)
    assert transactions == sample.transactions
