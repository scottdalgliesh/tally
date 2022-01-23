from copy import deepcopy
from datetime import date

import pandas as pd
from sqlalchemy import select

from ..auth.models import User
from ..extensions import db
from .models import Bill, Category


class UserBillData:
    """
    A class used to retrieve and manipulate transaction data for the specified user.

    Attributes
    ----------
    data : pd.DataFrame
        A pandas.Dataframe containing retrieved and filtered transaction data.

    Methods
    -------
    filter_first_and_last_month()
        Filter out data from the first and last month on record, which may be incomplete.
    filter_by_category(category: str)
        Filter out all data which does not match the specified category.
    summarize()
        Returns a pivot table summary of transaction data, indexed by month and category.

    """

    def __init__(self, user: User, show_hidden: bool = False) -> None:
        """Retrieve all data for the specified user as a dataframe, indexed by date."""
        # build a query for the user's data
        query = (
            select(Bill.date, Bill.descr, Bill.value, Category.name)
            .join(Bill.category)
            .where(Bill.user_id == user.id)
            .order_by(Bill.date)
        )
        if show_hidden is False:
            query = query.where(Category.hidden == False)  # pylint: disable=singleton-comparison

        # read query results into a dataframe
        user_data = pd.read_sql_query(
            sql=query,
            con=db.session.connection(),
            index_col="date",
            parse_dates="date",
        )
        user_data.rename(
            columns={"descr": "Description", "value": "Value", "name": "Category"},
            inplace=True,
        )
        user_data.index.rename("Date", inplace=True)
        self.data = user_data

    def filter_first_and_last_month(self) -> None:
        """Filter out data from the first and last month on record, which may be incomplete."""
        if self.data.empty:
            raise ValueError("Attempted to filter data from empty dataframe.")
        start_date = self.data.index[0] + pd.offsets.MonthBegin(1)
        end_date = self.data.index[-1] - pd.offsets.MonthEnd(1)
        if start_date > end_date:
            raise ValueError(
                "Error during data filtering. Insufficient data exists "
                "to filter out (potentially incomplete) first and last month's data."
            )
        start_date_filter = self.data.index >= start_date
        end_date_filter = self.data.index <= end_date
        self.data = self.data[start_date_filter & end_date_filter]

    def filter_by_category(self, category: str) -> None:
        """Filter out all data which does not match the specified category."""
        category_filter = self.data["Category"] == category
        self.data = self.data[category_filter]

    def summarize(self) -> pd.DataFrame:
        """Return a pivot table summary, indexed by month and category."""
        # create pivot table and sort by month (level=1) then year (level=0)
        data = deepcopy(self.data)
        data["Month"] = data.index.to_series().map(lambda row: row.strftime("%B"))
        data["Year"] = data.index.to_series().map(lambda row: row.year)
        months = {date(1, month, 1).strftime("%B"): month for month in range(1, 13)}
        pivot = pd.pivot_table(
            data,
            values="Value",
            columns="Category",
            aggfunc="sum",
            fill_value=0,
            index=["Year", "Month"],
        )
        pivot.sort_index(level=1, key=lambda index: index.map(months), inplace=True)
        pivot.sort_index(level=0, inplace=True, sort_remaining=False)

        # add category averages and month totals
        pivot.loc[("Average", ""), :] = pivot.mean(axis=0)
        pivot.sort_values(by=pivot.index[-1], axis=1, ascending=False, inplace=True)
        pivot["Total"] = pivot.sum(axis=1)
        return pivot
