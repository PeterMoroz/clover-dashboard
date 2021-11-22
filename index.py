from app import app
from app import server

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

from tabs import tab_p2p_inbound
from tabs import tab_p2p_outbound
from tabs import tab_transactions
from tabs import tab_cpu_usage
from tabs import tab_memory_usage

from datetime import datetime

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Clover blockchain analytics", className="header-title"
                ),
                html.P(
                    children="Analyze your node's activity",
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
                dcc.Tab(label="CPU usage", value="cpu-usage"),
                dcc.Tab(label="Memory usage", value="memory-usage"),
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
        return tab_p2p_inbound.layout
    elif tab == "p2p-outbound":
        return tab_p2p_outbound.layout
    elif tab == "transactions":
        return tab_transactions.layout
    elif tab == "cpu-usage":
        return tab_cpu_usage.layout
    elif tab == "memory-usage":
        return tab_memory_usage.layout



if __name__ == "__main__":
    app.run_server(debug=True)
