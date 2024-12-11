import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, Output, Input, State, html
from dash import ctx
from dash_extensions.javascript import assign, arrow_function
import json
import os

from sqlalchemy import create_engine
import pandas as pd

from Scatter_plot_dt_v3_dt import generate_geojson

import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import ALL

from functions import point_to_layer, style_function, hover_style, super_cluster_options, style_handle, hover_style, get_info,create_legend, legend_colors

empty_geojson = {
    "type": "FeatureCollection",
    "features": []
}

my_conn = create_engine("mysql+pymysql://root:JXXX62.171.178.235/ne_database")
global cell_layer
cell_layer = pd.read_sql('df_active', con=my_conn)

with open('./assets/layer_U09.json') as f:
   layer = json.load(f)


# Create small example app.
app = Dash()

info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "left": "10px", "zIndex": "1000"})
multi_polyline_positions = []

default_map_children = [
    dl.TileLayer(),
    dl.GeoJSON(data=layer, id="geojson",
               hideout=dict(selected=[]), style=style_handle,
               hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))
    ),
    dl.Polyline(positions=multi_polyline_positions, id='nbs'),
    dl.EasyButton(icon="fa-globe", title="Reset View", id="btn"),
    dl.LayerGroup(id="circle-container"),
    dl.LayerGroup(id="geojson2"),
    #dl.GeoJSON(id='test_map')
    dl.GeoJSON(
        id="test_map",
        data=empty_geojson,  # Initial empty data
        #cluster=True,  # Enable clustering
        zoomToBounds=False,
        options=dict(pointToLayer=point_to_layer),  # Use the JavaScript function
        hoverStyle=hover_style,  # Hover style function
        # superClusterOptions={
        #     "radius": 100,
        #     #"reduce": super_cluster_options
        # }
        style=style_function  # Dynamic style based on hideout
    )
]

app.layout = html.Div([
    html.Div([
        dl.Map(
            id="map",
            style={'width': '80%', 'height': '50vh'},
            center=[38.96, -9.3],
            zoom=12,
            children=default_map_children
        )
    ]),
    html.Div(id="log2"),
    html.Div(id="log"),
    dcc.Store(id="selected-legend-items", data=list(legend_colors.values())),  # Initialize with all colors selected
    html.Div(
        style={
            "position": "absolute",  # Position the legend absolutely relative to the parent
            "top": "10px",
            "right": "10px",
            "padding": "10px",
            "backgroundColor": "white",
            "boxShadow": "0px 0px 5px rgba(0,0,0,0.5)",
            "zIndex": "1000",
            "border": "1px solid black",
            "borderRadius": "5px",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "5px",
                    "cursor": "pointer",  # Add pointer to indicate interactivity
                },
                children=[
                    html.Div(
                        style={
                            "width": "20px",
                            "height": "20px",
                            "backgroundColor": color,
                            "marginRight": "10px",
                            "border": "1px solid black",
                        },
                        id={"type": "legend-item", "color": color}  # Unique ID for each legend item
                    ),
                    html.Span(label, style={"fontSize": "14px"}),
                ],
            )
            for label, color in legend_colors.items()
        ]
    ),
    info,
        html.Div([
        html.H3("RxLev Line Chart"),
        dcc.Graph(
            id="rxlev-chart",
            config={"displayModeBar": False},  # Hide extra controls for simplicity
            hoverData=None,  # Add hoverData for hover interactivity
            clickData=None   # Add clickData for click interactivity
            )
    ])
])

@app.callback(
    Output("geojson", "hideout"),
    Output("map", "viewport"),
    Output("nbs", "positions"),
    Input("geojson", "n_clicks"),
    State("geojson", "clickData"),
    State("geojson", "hideout"),
    prevent_initial_call=True)
def toggle_select(_, feature, hideout):
    selected = hideout["selected"]
    name = feature["properties"]["name"]
    if name in selected:
        selected.remove(name)
        view = dict(center=[41.1, -8.6], zoom=11, transition="flyTo")
        multi_polyline_positions = []
    else:
        selected.append(name)
        selected_cell = cell_layer[cell_layer['CELLNAME'] == name].reset_index()
        query = f"select * from nb_relations where SRC = '{name}' and Tech_x = 'UMTS900' and Tech_y = 'UMTS900'"
        selected_nbs = pd.read_sql(query, con=my_conn)
        selected_nbs_filter = selected_nbs[['SRC', 'TRG', 'LAT_x', 'LONG_x', 'LAT_y', 'LONG_y', 'ATT']]
        multi_polyline_positions = [
            [[row["LAT_x"], row["LONG_x"]], [row["LAT_y"], row["LONG_y"]]]
            for _, row in selected_nbs_filter.iterrows()
        ]
        lat1 = selected_cell['LAT'][0]
        lon1 = selected_cell['LONG'][0]
        view = dict(center=[lat1, lon1], zoom=15, transition="flyTo")
    return hideout, view, multi_polyline_positions

@app.callback(Output("info", "children"), Input("geojson", "hoverData"), prevent_initial_call=True)
def info_hover(feature):
    return get_info(feature)

# @app.callback(
#     # Output("geojson2", "children"),
#     [Output("test_map", "data"), Output("test_map", "key")],
#     Input("btn", "n_clicks"),
#     State("map", "bounds"),
#     prevent_initial_call=True
# )
# def log(n_clicks, bounds):
#     print("Callback triggered. Clicks:", n_clicks, "Bounds:", bounds)
#     geojson_data = generate_geojson(bounds)

#     print(json.dumps(geojson_data, indent=2))
 
#     geo_dumped=json.dumps(geojson_data, indent=4)
#     # print(geojson_data)
#     return geojson_data, f"geojson-{n_clicks}"

@app.callback(
    Output("rxlev-chart", "figure"),  # Updates the line chart
    Input("test_map", "clickData"),  # Triggered on click
    State("test_map", "data")  # Accesses GeoJSON data
)
def update_line_chart(clicked_feature, geojson_data):
    if not clicked_feature or not geojson_data:
        return go.Figure()

    # Extract all features from the GeoJSON
    features = geojson_data["features"]

    # Find the index of the clicked feature
    clicked_index = next(
        (i for i, f in enumerate(features) if f["properties"] == clicked_feature["properties"]), None
    )
    if clicked_index is None:
        return go.Figure()

    # Select 20 points before and after the clicked feature
    start = max(clicked_index - 20, 0)
    end = min(clicked_index + 20, len(features))
    selected_features = features[start:end]

    # Prepare data for the chart
    x = list(range(start, end))  # Sequence numbers
    y = [f["properties"]["RxLev"] for f in selected_features]  # RxLev values

    # Create the line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name="RxLev"))
    fig.update_layout(
        title="RxLev Values Around Clicked Point",
        xaxis_title="Point Sequence",
        yaxis_title="RxLev",
        template="plotly_white"
    )
    return fig

@app.callback(
    Output("test_map", "hideout"),  # Use the hideout to manage highlighted features
    [Input("rxlev-chart", "hoverData")],  # Triggered on chart hover
    State("test_map", "data")  # Access the GeoJSON data
)
def highlight_point_on_map(hover_data, geojson_data):
    if not hover_data or not geojson_data:
        return {"highlighted": None}  # Clear any highlights if no hover data

    # Get the x-axis (point sequence) index from hoverData
    hovered_index = hover_data["points"][0]["x"]

    # Locate the corresponding feature in the GeoJSON data
    features = geojson_data["features"]
    if 0 <= hovered_index < len(features):
        highlighted_feature = features[hovered_index]
        # Return the highlighted feature's ID or a unique identifier to the map
        return {"highlighted": highlighted_feature["properties"]["id"]}

    return {"highlighted": None}  # Clear highlight if no match is found

@app.callback(
    Output("selected-legend-items", "data"),
    Input({"type": "legend-item", "color": ALL}, "n_clicks"),
    State("selected-legend-items", "data"),
    prevent_initial_call=True
)
def update_legend_selection(n_clicks_list, selected_items):
    triggered_id = ctx.triggered_id  # Get the ID of the triggered item
    if not triggered_id or triggered_id["type"] != "legend-item":
        return selected_items  # Return current state if no valid click

    clicked_color = triggered_id["color"]
    if clicked_color in selected_items:
        # Remove the color if already selected (filter out its circles)
        selected_items.remove(clicked_color)
    else:
        # Add the color if not selected (restore its circles)
        selected_items.append(clicked_color)

    return selected_items

@app.callback(
    Output("test_map", "data"),
    [Input("selected-legend-items", "data"),
     Input("btn", "n_clicks")],
    [State("test_map", "data"),
     State("map", "bounds")]
)
def update_geojson(selected_colors, btn_clicks, geojson_data, bounds):
    triggered_id = ctx.triggered_id  # Get the ID of the triggering input

    if triggered_id == "selected-legend-items":
        # Toggle the `hidden` property for features
        for feature in geojson_data["features"]:
            if feature["properties"]["color"] in selected_colors:
                feature["properties"]["hidden"] = False  # Restore visible circles
            else:
                feature["properties"]["hidden"] = True  # Hide circles

        print("Updated Features:", geojson_data["features"])  # Debugging
        return geojson_data

    elif triggered_id == "btn":
        # Regenerate GeoJSON data on button click
        geojson_data = generate_geojson(bounds)
        return geojson_data

    return geojson_data  # Default to current data


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8051)