from dash import Dash, Input, Output, dcc, html

app = Dash(__name__)

app.layout = html.Div([
    dcc.Input(id="input-a", type="number", value=1),
    dcc.Input(id="input-b", type="number", value=2),
    html.Div(id="output"),
])

app.clientside_callback(
    """
    function(a, b) {
        return window.dash_clientside.my_filtering.test(a, b);
    }
    """,
    Output("output", "children"),
    [Input("input-a", "value"), Input("input-b", "value")]
)

if __name__ == "__main__":
    app.run_server(debug=True)