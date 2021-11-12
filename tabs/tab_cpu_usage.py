import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
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
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  trace0 = go.Scatter(
    x = df["date_time"], y = df["kernel"], name="kernel", mode="lines", line=dict(color="#00A378"))
  trace1 = go.Scatter(
    x = df["date_time"], y = df["user"], name="user", mode="lines", line=dict(color="#0085AF"))

  data = [trace0, trace1]
  layout = go.Layout(title="CPU usage", 
                    yaxis=dict(title="% of total load", zeroline=False),
                    xaxis=dict(title="date-time", zeroline=False))
  figure = go.Figure(data=data, layout=layout)
  return figure
