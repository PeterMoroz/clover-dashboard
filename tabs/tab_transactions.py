import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import dash_table
from dash.dependencies import Output, Input

from app import app

import pandas as pd


dataframe = pd.read_csv("datasets/transactions.csv")
dataframe["date_time"] = pd.to_datetime(dataframe["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)


tx_status_names = {0: "Success", 1: "Pending", 2: "Bad Query Form", 3: "Bad Sign", 4: "Not Enough Balance", 5: "Revert", 6: "Failed"}

tx_statuses2 = [ {"value": 0, "label": "Success"},
                {"value": 1, "label": "Pending"},
                {"value": 2, "label": "Bad Query Form"},
                {"value": 3, "label": "Bad Sign"}, 
                {"value": 4, "label": "Not Enough Balance"},
                {"value": 5, "label": "Revert"},
                {"value": 6, "label": "Failed"} ]

tx_types_names = {1: "Transfer", 2: "ContractCall", 3: "ContractCreation"}

layout = html.Div([
        html.H1("Transactions"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Status ", className="menu-title"),
                        dcc.Dropdown(
                            id="tx-status-filter",
                            options=tx_statuses2,
                            value=[0],
                            multi=True,
                            clearable=False,
                            className="dropdown",),
                    ]
                ),
            ],
        ),        
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="transactions", config={"displayModeBar": False},),
                    className="card"
                )
            ]
       ),

       html.Div(
          children=[
              html.Div(
                  children=[
                      html.Div(
                          children=dcc.Graph(id="transactions-pie-status", config={"displayModeBar": False}, ), className="card")
                  ], style = {"padding": 10, "flex": 1}
              ),
              html.Div(
                  children=[
                      html.Div(
                          children=dcc.Graph(id="transactions-pie-type", config={"displayModeBar": False}, ), className="card")
                  ], style = {"padding": 10, "flex": 1}
              ),
          ], style = {"display": "flex", "flex-direction": "row"}),
       html.Div(children=[html.Table(id="tx-table"), html.Div(id="tx-table-output")]),
    ]
)


@app.callback(Output("transactions", "figure"),
            [Input("tx-status-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_transactions_figure(statuses, start_date, end_date): 
  figure = {}
  df = dataframe.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]  
  trace = []
  for status in statuses:
    trace.append(go.Scatter(x=df[df.status == status]["date_time"],
                            y=df[df.status == status]["amount"],
                            mode="lines",
                            opacity=0.7,
                            name=tx_status_names[status],
                            textposition="bottom center"))
  traces = [trace]
  data = [val for sublist in traces for val in sublist]
  figure = {"data": data,
    "layout": go.Layout(
      colorway=["#1E90FF", "#FF8C00", "#228B22", "#FF4500", "#9370DB", "#A52A2A", "#DDA0DD"],
      margin={"b": 15},
      hovermode="x",
      autosize=True,
      title={"text": "Transactions", "font": {"color": "black"}, "x": 0.5},
      xaxis={"range": [df["date_time"].min(), df["date_time"].max()]},
      yaxis={"title": "amount"},
    ),
  }  
  return figure

@app.callback(Output("transactions-pie-status", "figure"),
            [Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_transactions_pie_status(start_date, end_date): 
  figure = {}
  df = dataframe.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  df = df.groupby("status").sum().reset_index()
  colorway=["#1E90FF", "#FF8C00", "#228B22", "#FF4500", "#9370DB", "#A52A2A", "#DDA0DD"]
  trace = go.Pie(labels=df["status"].map(tx_status_names), values=df.amount,
                marker=dict(colors=["#1E90FF", "#FF8C00", "#228B22", "#FF4500", "#9370DB", "#A52A2A", "#DDA0DD"],
                            line=dict(color="white", width=1)), hoverinfo="label+percent")                             
  return go.Figure(data=[trace])

@app.callback(Output("transactions-pie-type", "figure"),
            [Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_transactions_pie_type(start_date, end_date): 
  figure = {}
  df = dataframe.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  df = df.groupby("type").sum().reset_index()
  colorway=["#1E90FF", "#FF8C00", "#228B22", "#FF4500", "#9370DB", "#A52A2A", "#DDA0DD"]
  trace = go.Pie(labels=df["type"].map(tx_types_names), values=df.amount,
                # marker=dict(colors=["#1E90FF", "#FF8C00", "#228B22", "#FF4500", "#9370DB", "#A52A2A", "#DDA0DD"],
                marker=dict(colors=["#FF8C00", "#228B22", "#9370DB"],
                            line=dict(color="white", width=1)), hoverinfo="label+percent")                             
  return go.Figure(data=[trace])

@app.callback(Output("tx-table-output", "children"),
            [Input("tx-status-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_transactions_figure(statuses, start_date, end_date):
  df = dataframe.copy(deep=True)
  # df.drop("type", axis=1, inplace=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  statuses.sort()
  df = df[(df.status >= statuses[0]) & (df.status <= statuses[-1])]
  df["status"] = df["status"].map(tx_status_names)
  df["type"] = df["type"].map(tx_types_names)
  df = df[["date_time", "type", "status", "amount"]]
  df.rename(columns={"date_time": "Date Time", "type": "Type", "status": "Status", "amount": "Amount"}, inplace=True)

  data_table = dash_table.DataTable(
      id="tx-table-data",
      data=df.to_dict("records"),
      columns=[{"id": c, "name": c} for c in df.columns],
      style_table={"overflowY": "scroll"},
      style_cell={"width": "100px"},
      style_header={
          "backgroundColor": "rgb(230, 230, 230)",
          "fontWeight": "bold"
      }
  )
  return data_table
