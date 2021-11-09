import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from dash.dependencies import Output, Input

from app import app

import pandas as pd


dataframe = pd.read_csv("datasets/p2p_outbound.csv")
dataframe["date_time"] = pd.to_datetime(dataframe["timestamp"], unit='s')
dataframe.drop("timestamp", axis=1, inplace=True)
dataframe.sort_values("date_time", inplace=True)

peers = dataframe.peer_addr.unique()
peers = sorted(peers, key = lambda ip: [int(ip) for ip in ip.split('.')])
peers.insert(0, "all-peers")

layout = html.Div([
        html.H1("P2P outbound traffic"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Peer IP ", className="menu-title"),
                        dcc.Dropdown(
                            id="peer-out-filter",
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
                        id="outbound-traffic", config={"displayModeBar": False},),
                    className="card"
                )
            ]
       ),
       html.Div(children=[html.Table(id="p2p-out-table"), html.Div(id="p2p-out-table-output")]),
    ]
)


@app.callback(Output("outbound-traffic", "figure"),
            [Input("peer-out-filter", "value"), 
            Input("date-range", "start_date"), 
            Input("date-range", "end_date")])
def update_p2p_out_figure(peer, start_date, end_date):
  df = dataframe
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


@app.callback(Output("p2p-out-table-output", "children"),
            [Input("peer-out-filter", "value"),
            Input("date-range", "start_date"),
            Input("date-range", "end_date")])
def update_p2p_out_table(peer, start_date, end_date):
  df = dataframe.copy(deep=True)
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

