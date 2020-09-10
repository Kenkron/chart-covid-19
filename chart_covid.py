#!/usr/bin/env python3

import requests
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta

def make_url(service, fields, end_datetime=datetime.today()):
    end_time_string = end_datetime.strftime("%Y-%m-%d")
    fields_string = "%2C".join(fields)
    url = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/"
    url += service
    url += "/FeatureServer/0/query?f=json&"
    url += "where=Date%20IS%20NOT%20NULL%20AND%20Date%3Ctimestamp%20%27"
    url += end_time_string + "%2004%3A00%3A00%27&"
    url += "outFields=" + fields_string
    url += "&orderByFields=Date%20asc&resultType=standard"
    return url

CASES_URL = make_url("Florida_COVID_19_Cases_by_Day_For_Time_Series", ["Frequency", "Date"])

DEATHS_URL = make_url("Florida_COVID_19_Deaths_by_Day", ["Deaths", "Date"])

cases_request = requests.get(CASES_URL)
cases_json = cases_request.json()

deaths_request = requests.get(DEATHS_URL)
deaths_json = deaths_request.json()

# Populate day-by-day data
daily_new_cases = {}
for feature in cases_json["features"]:
    entry = feature["attributes"]
    if entry["Date"] in daily_new_cases:
        daily_new_cases[entry["Date"]] += entry["FREQUENCY"]
    else:
        daily_new_cases[entry["Date"]] = entry["FREQUENCY"]

daily_deaths = {}
for feature in deaths_json["features"]:
    entry = feature["attributes"]
    if entry["Date"] in daily_deaths:
        daily_deaths[entry["Date"]] += entry["Deaths"]
    else:
        daily_deaths[entry["Date"]] = entry["Deaths"]

# Plot a bar chart of the data
case_times = list(daily_new_cases.keys())
case_times.sort()
death_times = list(daily_deaths.keys())
death_times.sort()

# Daily new case data:
NEW_CASES = list(map(lambda x: daily_new_cases[x], case_times))
DEATHS = list(map(lambda x: daily_deaths[x], death_times))
# To prevent confusion, make sure the deaths graph is as long as the new cases graph
if (case_times[-1] not in death_times):
    death_times.append(case_times[-1])
    daily_deaths[death_times[-1]] = -1

DATES = list(map(lambda x: datetime.fromtimestamp(x/1000), case_times))
DEATH_DATES =  list(map(lambda x: datetime.fromtimestamp(x/1000), death_times))

BUFFER = 2

new_case_graph = go.Bar(name="New Cases", x = DATES[:-BUFFER], y = NEW_CASES[:-BUFFER], marker_color="lightblue")
deaths_graph = go.Bar(name="Deaths", x = DEATH_DATES[:-BUFFER], y = DEATHS[:-BUFFER], marker_color="darkred")

# 3 Day moving average:

def getMovingSum(data, span):
    sums = []
    for i in range(len(data)):
        acc = sum(data[max(0, i + 1 - span) : i + 1])
        sums.append(acc)
    return sums

def getMovingAverage(data, span):
    sums = getMovingSum(data, span)
    return list(map(lambda x: x/span, sums))

moving_avg_span = 5
moving_avg = getMovingAverage(NEW_CASES, moving_avg_span)
moving_avg_graph = go.Scatter(
    # Mention the timespan in the name
    name=str(moving_avg_span) + " Day Moving Average",
    # Line it up so that each data point is in the middle of its averaged samples
    x = DATES[:-int(moving_avg_span/2)], y = moving_avg[int(moving_avg_span/2):],
    line_color = "green")

# 11 Day moving average:
# Because the disease lasts about 11 days, this should refelct about
# 1/11 of current cases, so multiplying it by 11 should give us the actual sum

moving_sum_span = 11
moving_sum = getMovingSum(NEW_CASES, moving_sum_span)
moving_sum_graph = go.Scatter(name=str(moving_sum_span) + " Day Sum", x = DATES, y = moving_sum, line_color = "crimson")

figure = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=[
        "Florida COVID-19: 11 Day Sum",
        "Florida COVID-19: New Cases",
        "Florida COVID-19: Deaths"
    ]
)
figure.add_trace(moving_sum_graph, row=1, col=1)
figure.add_trace(new_case_graph, row=2, col=1)
figure.add_trace(deaths_graph, row=3, col=1)
figure.add_trace(moving_avg_graph, row=2, col=1)

figure.show()
