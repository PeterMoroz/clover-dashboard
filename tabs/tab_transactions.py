import dash
import dash_core_components as dcc
import dash_html_components as html

tx_statuses = {0: "Success", 1: "Pending", 2: "Bad Query Form", 3: "Bad Sign", 4: "Not Enough Balance", 5: "Revert", 6: "Failed", 255: "all-transactions"}

layout_transactions = html.Div([
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

