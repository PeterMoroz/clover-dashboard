import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

from app import app

import pandas as pd


dataframe = pd.read_csv("datasets/cpu_usage.csv")
dataframe["date_time"] = pd.to_datetime(dataframe["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)


layout = html.Div([
        html.H1("CPU usage"),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="cpu-usage-graph", config={"displayModeBar": False},),
                    className="card"
                )
            ]
       ),
    ]
)

@app.callback(Output("cpu-usage-graph", "figure"),
            [Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_cpu_usage_figure(start_date, end_date):
  df = dataframe
  data = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  figure = {
      "data": [
          {"x": data["date_time"], "y": data["kernel"], "type": "lines", "name": "kernel"},
          {"x": data["date_time"], "y": data["user"], "type": "lines", "name": "user"},
      ],
      "layout": {
          "title": {
              "text": "CPU usage",
              "x": 0.05,
              "xanchor": "left",
              "xaxis": {"fixedrange": True},
          },
      },
  }
  return figure
