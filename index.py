from app import app
from app import server

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input

from tabs import tab_p2p_inbound
from tabs import tab_p2p_outbound
from tabs import tab_transactions


import pandas as pd
from datetime import datetime


p2p_in_df = pd.read_csv("data/p2p_inbound.csv")
p2p_in_df["date_time"] = pd.to_datetime(p2p_in_df["timestamp"], unit='s')
p2p_in_df.drop("timestamp", axis=1, inplace=True)
p2p_in_df.sort_values("date_time", inplace=True)

p2p_out_df = pd.read_csv("data/p2p_outbound.csv")
p2p_out_df["date_time"] = pd.to_datetime(p2p_out_df["timestamp"], unit='s')
p2p_out_df.drop("timestamp", axis=1, inplace=True)
p2p_out_df.sort_values("date_time", inplace=True)

transactions_df = pd.read_csv("data/transactions.csv")
transactions_df["date_time"] = pd.to_datetime(transactions_df["timestamp"], unit='s')
transactions_df.drop("timestamp", axis=1, inplace=True)
tx_status_names = {0: "Success", 1: "Pending", 2: "Bad Query Form", 3: "Bad Sign", 4: "Not Enough Balance", 5: "Revert", 6: "Failed"}


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Clover blockchain analytics", className="header-title"
                ),
                html.P(
                    children="Analyze P2P traffic of your nodes",
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div(
            children=[
                html.Div(children="Date Range", className="menu-title"),
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed=datetime(2019, 11, 21),
                    max_date_allowed=datetime.now(),
                    start_date=datetime(2021, 1, 1),
                    end_date=datetime.now(),),
            ],
            className="menu"
        ),

        dcc.Tabs(id="multiple-tabs", value="transactions",
            children=[
                dcc.Tab(label="P2P inbound traffic", value="p2p-inbound"),
                dcc.Tab(label="P2P outbound traffic", value="p2p-outbound"),
                dcc.Tab(label="Transactions", value="transactions"),
            ]
        ),
        html.Div([html.Div(id="tabs-content")],
            style={"marginBottom": 50, "marginTop": 25}
        ),
        
    ],
    className="wrapper",
)

@app.callback(Output("tabs-content", "children"),
            [Input("multiple-tabs", "value")])
def render_content(tab):
    if tab == "p2p-inbound":
        return tab_p2p_inbound.layout_p2p_inbound
    elif tab == "p2p-outbound":
        return tab_p2p_outbound.layout_p2p_outbound
    elif tab == "transactions":
        return tab_transactions.layout_transactions

 
@app.callback(Output("inbound-traffic", "figure"),
            [Input("peer-in-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_p2p_in_figure(peer, start_date, end_date):
  data = p2p_in_df
  data = data[(data.date_time >= start_date) & (data.date_time <= end_date)]
  title = "Peer's IP "
  if peer != None and peer != "all-peers":
    data = data[data.peer_addr == peer]
    title += peer
  else:
    title = "All peers"     # TO DO: agregate data

  figure = {
      "data": [
          {"x": data["date_time"], "y": data["rd_count"], "type": "lines", "name": "read"},
          {"x": data["date_time"], "y": data["wr_count"], "type": "lines", "name": "written"},
      ],
      "layout": {
          "title": {
              "text": f"P2P inbound traffic.  {title}",
              "x": 0.05,
              "xanchor": "left",
              "xaxis": {"fixedrange": True},
          },
      },
  }
  return figure

@app.callback(Output("outbound-traffic", "figure"),
            [Input("peer-out-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_p2p_out_figure(peer, start_date, end_date):
  df = p2p_out_df
  data = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  title = "Peer's IP "
  if peer != None and peer != "all-peers":
    data = df[(df.date_time >= start_date) & (df.date_time <= end_date) & (data.peer_addr == peer)]
    title += peer
  else:
    title = "All peers" # TO DO: agregate data

  figure = {
      "data": [
          {"x": data["date_time"], "y": data["rd_count"], "type": "lines", "name": "read"},
          {"x": data["date_time"], "y": data["wr_count"], "type": "lines", "name": "written"},
      ],
      "layout": {
          "title": {
              "text": f"P2P outbound traffic. {title}",
              "x": 0.05,
              "xanchor": "left",
              "xaxis": {"fixedrange": True},
          },
      },
  }
  return figure

@app.callback(Output("transactions", "figure"),
            [Input("tx-status-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_transactions_figure(status, start_date, end_date): 
  figure = {}
  df = transactions_df
  data = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  status_colors = {0: "#1E90FF", 1: "#FF8C00", 2: "#228B22", 3: "#FF4500", 4: "#9370DB", 5: "#A52A2A", 6: "#DDA0DD"}
  if status != None and status != 255:
    data = data[data.status == status]
    name = tx_status_names[status]
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
                "xaxis": {"fixedrange": True},
            },
        },
    }
  else:
    figure = {
        "data": [
            {"x": data["date_time"], "y": data[data.status == 0]["amount"], 
              "type": "lines", "name": tx_status_names[0], "marker": { "color": status_colors[0]},},
            {"x": data["date_time"], "y": data[data.status == 1]["amount"], 
              "type": "lines", "name": tx_status_names[1], "marker": { "color": status_colors[1]},},
            {"x": data["date_time"], "y": data[data.status == 2]["amount"], 
              "type": "lines", "name": tx_status_names[2], "marker": { "color": status_colors[2]},},
            {"x": data["date_time"], "y": data[data.status == 3]["amount"], 
              "type": "lines", "name": tx_status_names[3], "marker": { "color": status_colors[3]},},
            {"x": data["date_time"], "y": data[data.status == 4]["amount"], 
              "type": "lines", "name": tx_status_names[4], "marker": { "color": status_colors[4]},},
            {"x": data["date_time"], "y": data[data.status == 5]["amount"], 
              "type": "lines", "name": tx_status_names[5], "marker": { "color": status_colors[5]},},
            {"x": data["date_time"], "y": data[data.status == 6]["amount"], 
              "type": "lines", "name": tx_status_names[6], "marker": { "color": status_colors[6]},},
        ],
        "layout": {
            "title": {
                "text": "All transactions",
                "x": 0.05,
                "xanchor": "left",
                "xaxis": {"fixedrange": True},
            },
        },
    }
  return figure


@app.callback(Output("p2p-in-table-output", "children"),
            [Input("peer-in-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_transactions_figure(peer, start_date, end_date):
  df = p2p_in_df.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  if peer != None and peer != "all-peers":
    df = df[df.peer_addr == peer]
    df.drop("peer_addr", axis=1, inplace=True)
    df = df[["date_time", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "rd_count": "Read bytes", "wr_count": "Written bytes"}, inplace=True)
  else:
    df = df[["date_time", "peer_addr", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "peer_addr": "Peer's IP", "rd_count": "Read bytes", "wr_count": "Written bytes"}, inplace=True)


  data_table = dash_table.DataTable(
      id="p2p-in-table-data",
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


@app.callback(Output("p2p-out-table-output", "children"),
            [Input("peer-out-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_transactions_figure(peer, start_date, end_date):
  df = p2p_out_df.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  if peer != None and peer != "all-peers":
    df = df[df.peer_addr == peer]
    df.drop("peer_addr", axis=1, inplace=True)
    df = df[["date_time", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "rd_count": "Read bytes", "wr_count": "Written bytes"}, inplace=True)
  else:
    df = df[["date_time", "peer_addr", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "peer_addr": "Peer's IP", "rd_count": "Read bytes", "wr_count": "Written bytes"}, inplace=True)


  data_table = dash_table.DataTable(
      id="p2p-out-table-data",
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


@app.callback(Output("tx-table-output", "children"),
            [Input("tx-status-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_transactions_figure(status, start_date, end_date):
  df = transactions_df.copy(deep=True)
  df.drop("type", axis=1, inplace=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  if status != None and status != 255:
      df = df[df.status == status]
      df.drop("status", axis=1, inplace=True)
      df = df[["date_time", "amount"]]
      df.rename(columns={"date_time": "Date Time", "amount": "Amount"}, inplace=True)
  else:
      df["status"] = df["status"].map(tx_status_names)
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

if __name__ == "__main__":
    app.run_server(debug=True)
