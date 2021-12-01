import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table

from dash.dependencies import Output, Input

from app import app

import pandas as pd


p2p_in_df = pd.read_csv("datasets/p2p_inbound.csv")
p2p_in_peers = p2p_in_df.peer_addr.unique()
p2p_in_peers = sorted(p2p_in_peers, key = lambda ip: [int(ip) for ip in ip.split('.')])
p2p_in_peers.insert(0, "all-peers")

dataframe = pd.read_csv("datasets/p2p_inbound.csv")
dataframe["date_time"] = pd.to_datetime(p2p_in_df["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)
dataframe.sort_values("date_time", inplace=True)

peers = dataframe.peer_addr.unique()
peers = sorted(peers, key = lambda ip: [int(ip) for ip in ip.split('.')])
peers.insert(0, "all-peers")


layout = html.Div([
        html.H1("P2P inbound traffic"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Peer IP ", className="menu-title"),
                        dcc.Dropdown(
                            id="peer-in-filter",
                            options=[{"label": ip, "value": ip} for ip in peers],
                            value=peers[0],
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
                        id="inbound-traffic", config={"displayModeBar": False},),
                    className="card"
                )
            ]
       ),
       html.Div(children=[html.Table(id="p2p-in-table"), html.Div(id="p2p-in-table-output")]),
    ]
)

@app.callback(Output("inbound-traffic", "figure"),
            [Input("peer-in-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_p2p_in_figure(peer, start_date, end_date):
  df = dataframe
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]
  title = "Peer's IP "
  if peer != None and peer != "all-peers":
    df = df[df.peer_addr == peer]
    title += peer
  else:
    title = "All peers"

  trace0 = go.Scatter(
    x = df["date_time"], y = df["rd_count"], name="ingress", mode="lines", line=dict(color="#FF8000"))
  trace1 = go.Scatter(
    x = df["date_time"], y = df["wr_count"], name="egress", mode="lines", line=dict(color="#09557F"))

  data = [trace0, trace1]
  layout = go.Layout(title="P2P inbound traffic", 
                    yaxis=dict(title="Bytes/s", zeroline=False),
                    xaxis=dict(title="date-time", zeroline=False))
  figure = go.Figure(data=data, layout=layout)

  return figure

@app.callback(Output("p2p-in-table-output", "children"),
            [Input("peer-in-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_p2p_in_table(peer, start_date, end_date):
  df = dataframe.copy(deep=True)
  df = df[(df.date_time >= start_date) & (df.date_time <= end_date)]

  if peer != None and peer != "all-peers":
    df = df[df.peer_addr == peer]
    df.drop("peer_addr", axis=1, inplace=True)
    df = df[["date_time", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "rd_count": "ingress (bytes/s)", "wr_count": "egress (bytes/s)"}, inplace=True)
  else:
    df = df[["date_time", "peer_addr", "rd_count", "wr_count"]]
    df.rename(columns={"date_time": "Date Time", "peer_addr": "Peer's IP", "rd_count": "ingress (bytes/s)", "wr_count": "egress (bytes/s)"}, inplace=True)

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
