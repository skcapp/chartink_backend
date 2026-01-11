import requests

BASE_URL = "https://chartink.com/screener/"
PROCESS_URL = BASE_URL + "process"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Put your saved screener name here
SAVED_SCREENER = "my-intraday-breakout"


def get_scan_clause():
    html = requests.get(BASE_URL + SAVED_SCREENER, headers=HEADERS).text
    start = html.find("scan_clause")
    start = html.find("'", start) + 1
    end = html.find("'", start)
    return html[start:end]


def fetch_stocks():
    scan_clause = get_scan_clause()
    res = requests.post(PROCESS_URL, headers=HEADERS, data={
                        "scan_clause": scan_clause}, timeout=10)
    data = res.json().get("data", [])
    return data[:10]  # return top 10
