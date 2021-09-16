#!/usr/bin/env python3

import requests
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta

# The latest few days have innacurate data. This is the number of
# entries to remove from the end of the bar graphs. (Min 1)
BUFFER = 1

CASES_URL = "https://jhucoronavirus.azureedge.net/api/v1/timeseries/us/cases/FL.json"
DEATHS_URL = "https://jhucoronavirus.azureedge.net/api/v1/timeseries/us/deaths/FL.json"

cases_request = requests.get(CASES_URL)
new_cases = cases_request.json()

deaths_request = requests.get(DEATHS_URL)
new_deaths = deaths_request.json()

# Plot a bar chart of the data
case_times = list(new_cases.keys())
case_times.sort()
death_times = list(new_deaths.keys())
death_times.sort()

# Daily new case data:
NEW_CASES = list(map(lambda x: new_cases[x]["raw_positives"], case_times))
DEATHS = list(map(lambda x: new_deaths[x]["raw_positives"], death_times))
# To prevent confusion, make sure the deaths graph is as long as the new cases graph
if (case_times[-1] not in death_times):
    death_times.append(case_times[-1])
    new_deaths[death_times[-1]] = -1

DATES = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d"), case_times))
DEATH_DATES =  list(map(lambda x: datetime.strptime(x, "%Y-%m-%d"), death_times))

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
