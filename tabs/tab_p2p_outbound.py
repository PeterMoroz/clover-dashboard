import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

p2p_out_df = pd.read_csv("data/p2p_outbound.csv")
p2p_out_peers = p2p_out_df.peer_addr.unique()
p2p_out_peers = sorted(p2p_out_peers, key = lambda ip: [int(ip) for ip in ip.split('.')])
p2p_out_peers.insert(0, "all-peers")

layout_p2p_outbound = html.Div([
        html.H1("P2P outbound traffic"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Peer IP ", className="menu-title"),
                        dcc.Dropdown(
                            id="peer-out-filter",
                            options=[{"label": ip, "value": ip} for ip in p2p_out_peers],
                            value=p2p_out_peers[0],
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

