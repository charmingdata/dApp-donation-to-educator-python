from dash import (
    Dash,
    html,
    callback,
    clientside_callback,
    Output,
    Input,
    State,
    no_update,
)
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_ag_grid as dag
import pandas as pd
from web3 import Web3

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    external_scripts=[{"src": "../static/signerinfo.js", "type": "module"}],
)
app.layout = dbc.Container(
    [
        html.H1("Donation-to-Educator dApp", style={"textAlign": "center"}),
        dbc.Alert(
            children="",
            id="tx-alert",
            is_open=False,
            duration=3000,
            style={"width": "50%"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Reason for donation:"),
                        dbc.Input(
                            id="insert-reason",
                            placeholder="Type a reason...",
                            type="text",
                            value="",
                            style={"width": 200},
                        ),
                    ],
                    width=5,
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Donation amount (wei):"),
                        dbc.Input(
                            id="insert-amount",
                            placeholder="Type amount...",
                            type="number",
                            value="",
                            style={"width": 200},
                        ),
                    ],
                    width=5,
                )
            ],
            className="mb-2",
        ),
        html.Div(
            style={"width": 200},
            children=[
                dmc.LoadingOverlay(
                    id="loading-effect",
                    children=dbc.Button(
                        "Submit",
                        id="submit-btn",
                        color="primary",
                        n_clicks=0,
                        className="mb-4",
                    ),
                    overlayOpacity=0.9,
                )
            ],
        ),
        dbc.Row(
            [
                html.Label("Go through the history of all donations:"),
            ]
        ),
        html.Div(
            style={"width": 300},
            children=[
                dmc.LoadingOverlay(
                    id="loading-effect2",
                    children=dbc.Button(
                        "See donations over 45 wei",
                        id="get-data",
                        color="info",
                        n_clicks=0,
                        className="mb-4",
                    ),
                    overlayOpacity=0.9,
                )
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Div(id="table-space", children="")],
                    width=4,
                ),
            ],
        ),
    ]
)


clientside_callback(
    """async function (n, v_reason, v_amount) {
         try { await checkNetwork();
         } catch (e) {console.log(e)}
         try {
         await sendTransaction(v_reason, v_amount);
         } catch (e) { return [window.dash_clientside.no_update, true, `Transaction Unsuccessful!`, 'danger']; }
         return [window.dash_clientside.no_update, true, `Donation of ${v_amount} wei Successful!`, 'success']
       }
    """,
    Output("loading-effect", "children"),
    Output("tx-alert", "is_open"),
    Output("tx-alert", "children"),
    Output("tx-alert", "color"),
    Input("submit-btn", "n_clicks"),
    State("insert-reason", "value"),
    State("insert-amount", "value"),
    prevent_initial_call=True,
)


@callback(
    Output("loading-effect2", "children"),
    Output("table-space", "children"),
    Input("get-data", "n_clicks"),
    prevent_initial_call=True,
)
def access_data(_):
    public_zkevm_rpc = "https://rpc.public.zkevm-test.net"
    w3 = Web3(Web3.HTTPProvider(public_zkevm_rpc))
    print(w3.is_connected())

    amount_list, reason_list = [], []
    event_signature = "LogData(uint256,string,address,uint256)"

    # Iterate over the blocks from earliest to latest (or a certain block number) and retrieve the event logs.
    # Adding a bigger range than 1000 blocks will take much more time to finish iterating.
    for block_number in range(1444600, 1444700):
        logs = w3.eth.get_logs(
            {
                "address": "0x98544219dd60eCc071302dAfBfce22F74334f244",
                "fromBlock": block_number,
                "toBlock": block_number,
                "topics": [w3.keccak(text=event_signature).hex()],
            }
        )

        for log in logs:
            # print(log)
            event_data = {
                "amount": int.from_bytes(log["topics"][1], byteorder="big"),
                "reason": w3.to_text(log["data"][-64:]),
            }

            print(event_data["amount"], event_data["reason"])

            if event_data["amount"] > 45:
                amount_list.append(event_data["amount"])
                reason_list.append(event_data["reason"])

    df = pd.DataFrame(list(zip(amount_list, reason_list)), columns=["WEI", "Reason"])

    grid = dag.AgGrid(
        id="our-table",
        className="ag-theme-alpine-dark",
        rowData=df.to_dict("records"),
        columnDefs=[{"field": i} for i in df.columns],
    )

    return no_update, grid


if __name__ == "__main__":
    app.run(debug=True)
