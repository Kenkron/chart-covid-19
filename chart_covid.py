#!/usr/bin/env python3

import requests
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime

time_str = datetime.now().strftime("%Y-%m-%d")

DATA_URL  = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/"
DATA_URL += "Florida_COVID_19_Cases_by_Day_For_Time_Series/FeatureServer/0/query?"
DATA_URL += "f=json&where=Date%20IS%20NOT%20NULL%20AND%20Date%3Ctimestamp%20%27" + time_str + "%2004%3A00%3A00%27&"
DATA_URL += "returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=ObjectId%2CFREQUENCY%2CDate&"
DATA_URL += "orderByFields=Date%20asc&resultOffset=0&resultRecordCount=32000&resultType=standard"

raw_request = requests.get(DATA_URL)
raw_json = raw_request.json()

# Populate day-by-day data
daily_new_cases = {}
for feature in raw_json["features"]:
	entry = feature["attributes"]
	if entry["Date"] in daily_new_cases:
		daily_new_cases[entry["Date"]] += entry["FREQUENCY"]
	else:
		daily_new_cases[entry["Date"]] = entry["FREQUENCY"]

# Plot a bar chart of the data
times = list(daily_new_cases.keys())
times.sort()

# Daily new case data:
NEW_CASES = list(map(lambda x: daily_new_cases[x], times))
DATES = list(map(lambda x: datetime.fromtimestamp(x/1000), times))

new_case_graph = go.Bar(name="New Cases", x = DATES, y = NEW_CASES, marker_color="lightblue")

# 3 Day moving average:

def getMovingAverage(data, span):
    averages = []
    for i in range(len(data)):
        acc = sum(data[max(0, i + 1 - span) : i + 1])
        averages.append(acc/span)
    return averages

moving_avg_span = 5
moving_avg = getMovingAverage(NEW_CASES, moving_avg_span)
moving_avg_graph = go.Scatter(name=str(moving_avg_span) + " Day Moving Average", x = DATES, y = moving_avg, line_color = "green")

# 12 Day moving average:
# Because the disease lasts about 12 days, this should refelct about
# 1/12 of current cases.

moving_sum_12 = list(map(lambda x: x*12, getMovingAverage(NEW_CASES, 12)))
moving_sum_12_graph = go.Scatter(name="12 Day Sum", x = DATES, y = moving_sum_12, line_color = "crimson")

figure = make_subplots(rows=2, cols=1, subplot_titles=["Florida COVID-19: Estimated Sick People", "Florida COVID-19: New Cases"])
figure.add_trace(moving_sum_12_graph, row=1, col=1)
figure.add_trace(new_case_graph, row=2, col=1)
figure.add_trace(moving_avg_graph, row=2, col=1)

figure.show()
