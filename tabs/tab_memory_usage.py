import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, Input

from app import app

import pandas as pd


dataframe = pd.read_csv("datasets/memory_usage.csv")
dataframe["date_time"] = pd.to_datetime(dataframe["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)


layout = html.Div([
        html.H1("Memory usage"),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="memory-usage-graph", config={"displayModeBar": False},),
                    className="card"
                )
            ]
       ),
    ]
)

@app.callback(Output("memory-usage-graph", "figure"),
            [Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_memory_usage_figure(start_date, end_date):
  df = dataframe
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  trace0 = go.Scatter(
    x = df["date_time"], y = df["virtual"], name="virtual", mode="lines", line=dict(color="#013848"))
  trace1 = go.Scatter(
    x = df["date_time"], y = df["physical"], name="physical", mode="lines", line=dict(color="#0085AF"))

  data = [trace0, trace1]
  layout = go.Layout(title="Memory usage", 
                    yaxis=dict(title="KBytes", zeroline=False),
                    xaxis=dict(title="date-time", zeroline=False))
  figure = go.Figure(data=data, layout=layout)
  return figure
