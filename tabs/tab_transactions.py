import dash
import dash_core_components as dcc
import dash_html_components as html

import dash_table
from dash.dependencies import Output, Input

from app import app

import pandas as pd


dataframe = pd.read_csv("datasets/transactions.csv")
dataframe["date_time"] = pd.to_datetime(dataframe["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)


tx_statuses = {0: "Success", 1: "Pending", 2: "Bad Query Form", 3: "Bad Sign", 4: "Not Enough Balance", 5: "Revert", 6: "Failed", 255: "all-transactions"}

layout = html.Div([
        html.H1("Transactions"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Status ", className="menu-title"),
                        dcc.Dropdown(
                            id="tx-status-filter",
                            options=[{"label": v, "value": k} for k, v in tx_statuses.items()],
                            value=255,
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
       html.Div(children=[html.Table(id="tx-table"), html.Div(id="tx-table-output")]),
    ]
)


@app.callback(Output("transactions", "figure"),
            [Input("tx-status-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_transactions_figure(status, start_date, end_date): 
  figure = {}
  df = dataframe.copy(deep=True)
  data = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  status_colors = {0: "#1E90FF", 1: "#FF8C00", 2: "#228B22", 3: "#FF4500", 4: "#9370DB", 5: "#A52A2A", 6: "#DDA0DD"}
  if status != None and status != 255:
    data = data[data.status == status]
    name = tx_statuses[status]
    color = status_colors[status]
    figure = {
        "data": [
            {"x": data["date_time"], "y": data["amount"], "type": "lines", "marker": { "color": f"{color}"}, },
        ],
        "layout": {
            "title": {
                "text": f"Transactions. Status: {name}",
                "x": 0.05,
                "xanchor": "left",
                # "xaxis": {"fixedrange": True},
            },
        },
    }
  else:
    data0 = data[data.status == 0]
    data1 = data[data.status == 1]
    data2 = data[data.status == 2]
    data3 = data[data.status == 3]
    data4 = data[data.status == 4]
    data5 = data[data.status == 5]
    data6 = data[data.status == 6]

    figure = {
        "data": [
            {"x": data0["date_time"], "y": data0["amount"], 
              "type": "lines", "name": tx_statuses[0], "marker": { "color": status_colors[0]},},
            {"x": data1["date_time"], "y": data1["amount"], 
              "type": "lines", "name": tx_statuses[1], "marker": { "color": status_colors[1]},},
            {"x": data2["date_time"], "y": data2["amount"], 
              "type": "lines", "name": tx_statuses[2], "marker": { "color": status_colors[2]},},
            {"x": data3["date_time"], "y": data3["amount"], 
              "type": "lines", "name": tx_statuses[3], "marker": { "color": status_colors[3]},},
            {"x": data4["date_time"], "y": data4["amount"], 
              "type": "lines", "name": tx_statuses[4], "marker": { "color": status_colors[4]},},
            {"x": data5["date_time"], "y": data5["amount"], 
              "type": "lines", "name": tx_statuses[5], "marker": { "color": status_colors[5]},},
            {"x": data6["date_time"], "y": data6["amount"], 
              "type": "lines", "name": tx_statuses[6], "marker": { "color": status_colors[6]},},
        ],
        "layout": {
            "title": {
                "text": "All transactions",
                "x": 0.05,
                "xanchor": "left",
                # "xaxis": {"fixedrange": True},
            },
        },
    }
  return figure


@app.callback(Output("tx-table-output", "children"),
            [Input("tx-status-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_transactions_figure(status, start_date, end_date):
  df = dataframe.copy(deep=True)
  df.drop("type", axis=1, inplace=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  if status != None and status != 255:
      df = df[df.status == status]
      df.drop("status", axis=1, inplace=True)
      df = df[["date_time", "amount"]]
      df.rename(columns={"date_time": "Date Time", "amount": "Amount"}, inplace=True)
  else:
      df["status"] = df["status"].map(tx_statuses)
      df = df[["date_time", "status", "amount"]]
      df.rename(columns={"date_time": "Date Time", "status": "Status", "amount": "Amount"}, inplace=True)

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
