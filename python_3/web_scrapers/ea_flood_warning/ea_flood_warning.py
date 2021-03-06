# -*- coding: utf-8 -*-

import datetime
import time
import requests
import zipfile
import os


class fetch_ea_rg:

    base_url = "http://environment.data.gov.uk/flood-monitoring/archive/readings-{}.csv"

    def __init__(self, date=None, year=None, month=None, day=None, dir_out=""):
        if date is not None:
            self.date = date
        elif year is not None and month is not None and day is not None:
            self.date = datetime.date(year, month, day)
        else:
            raise ValueError("No valid date set.")

        self.dir_out = dir_out
        self.base_raw = r"readings-{}.csv"
        self.base_file = os.path.join(dir_out, r"readings-{}.csv")
        self.base_zip = os.path.join(dir_out, r"readings-{}.zip")

    def gen_url(self):
        return self.base_url.format(self.date.isoformat())

    def gen_file(self):
        return self.base_raw.format(self.date.isoformat())

    def gen_file_name(self):
        return self.base_file.format(self.date.isoformat())

    def gen_zip_name(self):
        return self.base_zip.format(self.date.strftime("%Y-%m"))

    def fetch_data(self):
        """Download the data as a csv."""
        if not self.is_in_dir():
            self.data = requests.get(self.gen_url(), allow_redirects=True)
            with open(self.gen_file_name(), "wb") as f:
                f.write(self.data.content)

    def fetch_to_zip(self):
        """Fetch a day's worth of data and move it direct to the archive."""
        if not self.is_in_zip():
            self.fetch_data()
            self.move_to_zip()

    def add_days(self, ndays=1):
        """Add a number of days to the target date."""
        self.date += datetime.timedelta(days=ndays)

    def move_to_zip(self, remove_original=True):
        """Move a file from the download path to the zip archive."""
        if not self.is_in_zip():
            with zipfile.ZipFile(self.gen_zip_name(), mode="a") as zf:
                zf.write(
                    filename=self.gen_file_name(),
                    arcname=self.gen_file(),
                    compress_type=zipfile.ZIP_DEFLATED,
                )
            if remove_original:
                os.remove(self.gen_file_name())

    def is_in_dir(self):
        return os.path.isfile(self.gen_file_name())

    def is_in_zip(self):
        if not os.path.exists(self.gen_zip_name()):
            return False

        with zipfile.ZipFile(self.gen_zip_name(), mode="r") as zf:
            return self.gen_file() in zf.namelist()

    def is_fetched(self):
        return self.is_in_dir() or self.is_in_zip()

    def fetch_seq(self, days, forwards=True):
        """Fetch a sequence of days."""
        for x in range(days):
            print(self.date)
            self.fetch_to_zip()
            if forwards:
                self.add_days(1)
            else:
                self.add_days(-1)
            time.sleep(5)


# ==============================================================================
if __name__ == "__main__":
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    test = fetch_ea_rg(date=start_date, dir_out=r"_output_")
    test.fetch_seq(3, False)
 