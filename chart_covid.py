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
    rows=2,
    cols=1,
    subplot_titles=[
        "Florida COVID-19: Estimated Sick People",
        "Florida COVID-19: New Cases"
    ]
)
figure.add_trace(moving_sum_graph, row=1, col=1)
figure.add_trace(new_case_graph, row=2, col=1)
figure.add_trace(moving_avg_graph, row=2, col=1)

figure.show()
