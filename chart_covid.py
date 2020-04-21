#!/usr/bin/env python3

import requests
import plotly.graph_objects as go
from datetime import datetime

DATA_URL  = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/"
DATA_URL += "Florida_COVID_19_Cases_by_Day_For_Time_Series/FeatureServer/0/query?"
DATA_URL += "f=json&where=Date%20IS%20NOT%20NULL%20AND%20Date%3Ctimestamp%20%272020-04-21%2004%3A00%3A00%27&"
DATA_URL += "returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=ObjectId%2CFREQUENCY%2CDate&"
DATA_URL += "orderByFields=Date%20asc&resultOffset=0&resultRecordCount=32000&resultType=standard&cacheHint=true"

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

new_case_graph = go.Bar(name="New Cases", x = DATES, y = NEW_CASES)

# 3 Day moving average:

def getMovingAverage(data, span):
    averages = []
    for i in range(len(data)):
        acc = sum(data[max(0, i + 1 - span) : i + 1])
        averages.append(acc/span)
    return averages
moving_avg_3 = getMovingAverage(NEW_CASES, 3)
moving_avg_3_graph = go.Scatter(name="3 Day Moving Average", x = DATES, y = moving_avg_3, line_color = "green")

# 12 Day moving average:
# Because the disease lasts about 12 days, this should refelct about
# 1/12 of current cases.

moving_sum_12 = list(map(lambda x: x*12, getMovingAverage(NEW_CASES, 12)))
moving_sum_12_graph = go.Scatter(name="12 day sum\n(Estimated Sick People)", x = DATES, y = moving_sum_12, line_color = "crimson")

figure = go.Figure(
    data=[new_case_graph, moving_avg_3_graph, moving_sum_12_graph],
    layout_title_text="Florida COVID-19 Data"
)
figure.update_layout(legend={"x":0, "y":1})
figure.show()
