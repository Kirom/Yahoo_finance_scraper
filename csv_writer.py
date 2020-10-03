"""Helper module for writing csv file with historical data."""
import datetime

import os

from pathlib import Path


class CsvWriter:
    """Csv writer class."""

    def __init__(self, csv_text, company_name):
        """Initialize writer's instance."""
        self.csv_text = csv_text
        self.company_name = company_name
        self.list_of_rows = [
            column
            for column in map(
                lambda x: x.split(","), [row for row in csv_text.split("\n")]
            )
        ]
        self.result_dict = {}
        self.indexes_dates_dict = {}
        self.three_days_delta_indexes_list = []
        self.csv_result_string = (
            "Date,Open,High,Low,Close,Adj Close,Volume,3day_before_change\n"
        )

    def make_dicts(self):
        """Initialize result_dict and indexes_dates_dict."""
        for i in range(1, len(self.list_of_rows)):
            year = self.list_of_rows[i][0]
            other_data = self.list_of_rows[i][1:]
            other_data.append("-")
            self.result_dict[year] = other_data
            self.indexes_dates_dict[i] = year

    def make_deltas_list(self):
        """Make list of date deltas and their indexes."""
        for index_1, year_1 in self.indexes_dates_dict.items():
            for index_2, year_2 in self.indexes_dates_dict.items():
                first_iteration_date = datetime.date.fromisoformat(year_1)
                second_iteration_date = datetime.date.fromisoformat(year_2)
                first_date_index = index_1
                second_date_index = index_2
                delta = second_iteration_date - first_iteration_date
                if delta.days == 3:
                    self.three_days_delta_indexes_list.append(
                        [first_date_index, second_date_index]
                    )

    def make_result_dict(self):
        """Make result_dict."""
        for i in range(len(self.three_days_delta_indexes_list)):
            first_date_close = float(
                self.result_dict[
                    self.indexes_dates_dict[self.three_days_delta_indexes_list[i][0]]
                ][3]
            )
            second_date_close = float(
                self.result_dict[
                    self.indexes_dates_dict[self.three_days_delta_indexes_list[i][1]]
                ][3]
            )
            close_delta = first_date_close / second_date_close
            self.result_dict[
                self.indexes_dates_dict[self.three_days_delta_indexes_list[i][0]]
            ][-1] = str(close_delta)

    def extend_csv_result_string(self):
        """Complete csv_result_string."""
        for key, val in self.result_dict.items():
            self.csv_result_string += key + "," + ",".join(val) + "\n"
        self.csv_result_string = self.csv_result_string[:-1]

    def write_csv(self):
        """Write csv file."""
        file_name = f'{self.company_name}.csv'
        if not os.path.exists('results'):
            os.mkdir('results')
        with open(f"results/{file_name}", "w") as csv_file:
            csv_file.write(self.csv_result_string)

    def run(self):
        """Run csv writer."""
        self.make_dicts()
        self.make_deltas_list()
        self.make_result_dict()
        self.extend_csv_result_string()
        self.write_csv()
