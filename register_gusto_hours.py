#! /usr/bin/env python

"""
Usage:
1) $ chromium --remote-debugging-port=5555 https://manage.gusto.com/time_tracking &
2) Log into Gusto manually.
3) $ python register_gusto_hours.py < hours.json
"""

from datetime import date, datetime
import json
import sys
import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def main():
    json_data = json.load(sys.stdin)

    intervals_by_date = {}
    for (d_ts, intervals) in json_data.items():
        d = date.fromtimestamp(int(d_ts))
        intervals = [
            (datetime.fromtimestamp(start), datetime.fromtimestamp(end))
            for (start, end) in intervals
        ]
        intervals_by_date[d] = intervals

    register_hours(intervals_by_date)


def register_hours(intervals_by_date):
    options = ChromeOptions()
    options.add_experimental_option('debuggerAddress', 'localhost:5555')

    driver = Chrome(options=options)
    rows = driver.find_elements_by_class_name('timesheet-table-row')

    for row in rows:
        date_div = row.find_elements_by_class_name('timesheet-table-day-item')[-1]
        dt = datetime.strptime(date_div.text, '%b %d').replace(year=date.today().year).date()
        intervals = intervals_by_date.get(dt)
        if intervals is None:
            continue

        for (start, end) in intervals:
            add_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located(('css selector', 'div[role=button]')))
            add_button.click()

            el = driver.switch_to.active_element
            el.send_keys(start.strftime('%I'))  # hour
            el = driver.switch_to.active_element
            el.send_keys(start.strftime('%M'))  # minute
            el = driver.switch_to.active_element
            el.send_keys(start.strftime('%p'))  # am/pm

            el.send_keys(Keys.TAB)

            el = driver.switch_to.active_element
            el.send_keys(end.strftime('%I'))  # hour
            el = driver.switch_to.active_element
            el.send_keys(end.strftime('%M'))  # minute
            el = driver.switch_to.active_element
            el.send_keys(end.strftime('%p'))  # am/pm

            el.send_keys(Keys.ENTER)

            time.sleep(0.25)


if __name__ == '__main__':
    main()
