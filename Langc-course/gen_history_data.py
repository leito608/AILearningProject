import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests

START_YEAR_BE = 2550
END_DATE_BE = (2569, 11, 1)  # (year, month, day), the latest draw to collect
DRAW_DAYS = (1, 16, 17, 30)
URL = "https://news.sanook.com/lotto/check/{date}/"
OUTPUT_FILE = "lotto_history.csv"
HEADER = ["งวดวันที่", "วันในสัปดาห์", "เลข 2 ตัวที่ออกรางวัล"]
THAI_WEEKDAYS = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
TWO_DIGIT_PATTERN = re.compile(r"รางวัลเลขท้าย 2 ตัว[^\n]*?บาท(?:\s|\\r|\\n)*(\d{2})(?!\d)")


def candidate_dates():
    """Yield (day, month, year_be) from the newest date to the oldest."""
    end_year, end_month, end_day = END_DATE_BE
    for year in range(end_year, START_YEAR_BE - 1, -1):
        for month in range(12, 0, -1):
            for day in sorted(DRAW_DAYS, reverse=True):
                if (year, month, day) > (end_year, end_month, end_day):
                    continue
                try:
                    date(year - 543, month, day)
                except ValueError:
                    continue
                yield day, month, year


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        except requests.RequestException:
            time.sleep(1 + attempt)
            continue
        # Non-existing draws redirect to /lotto/ instead of returning 404
        if response.status_code == 200 and "/lotto/check/" in response.url:
            response.encoding = "utf-8"
            return response.text
        if response.status_code in (404, 410, 200):
            return None
        time.sleep(1 + attempt)
    return None


def scrape(day, month, year_be):
    date_key = f"{day:02d}{month:02d}{year_be}"
    html = fetch(URL.format(date=date_key))
    if html is None:
        return None
    match = TWO_DIGIT_PATTERN.search(html.replace("\r", ""))
    if not match:
        return None
    weekday = THAI_WEEKDAYS[date(year_be - 543, month, day).weekday()]
    return [f"{day:02d}/{month:02d}/{year_be}", weekday, match.group(1).zfill(2)]


def main():
    dates = list(candidate_dates())
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda item: scrape(*item), dates))

    rows = [row for row in results if row]
    # utf-8-sig lets Excel display the Thai text correctly
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"Saved {len(rows)} draws ({len(dates) - len(rows)} skipped) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
