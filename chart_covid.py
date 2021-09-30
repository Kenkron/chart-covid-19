#!/usr/bin/env python3

import requests
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta

# The latest few days have innacurate data. This is the number of
# entries to remove from the end of the bar graphs. (Min 1)
BUFFER = 10

CASES_URL = "https://jhucoronavirus.azureedge.net/api/v1/timeseries/us/cases/FL.json"
DEATHS_URL = "https://jhucoronavirus.azureedge.net/api/v1/timeseries/us/deaths/FL.json"

new_cases = requests.get(CASES_URL).json()

new_deaths = requests.get(DEATHS_URL).json()

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

moving_avg_span = 7
moving_avg = getMovingAverage(NEW_CASES[:-BUFFER], moving_avg_span)
moving_avg = getMovingAverage(moving_avg, moving_avg_span)
moving_avg_graph = go.Scatter(
    # Mention the timespan in the name
    name="Smoothed (double 7 day average)",
    # Line it up so that each data point is in the middle of its averaged samples
    x = DATES[:-int(moving_avg_span)-BUFFER], y = moving_avg[int(moving_avg_span):],
    line_color = "green")

figure = make_subplots(
    rows=2,
    cols=1,
    subplot_titles=[
        "Florida COVID-19: New Cases",
        "Florida COVID-19: Deaths"
    ]
)

figure.add_trace(new_case_graph, row=1, col=1)
figure.add_trace(moving_avg_graph, row=1, col=1)
figure.add_trace(deaths_graph, row=2, col=1)

figure.show()
