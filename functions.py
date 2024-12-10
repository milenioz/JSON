
from dash_extensions.javascript import assign, arrow_function
from dash import Dash, Output, Input, State, html


def get_color(rxlev):
    # Mapping ranges to their corresponding colors
    color_mapping = {
        -105: "#191919",
        -92: "#FF0800",
        -83: "#FF7300",
        -76: "#FFFF00",
        -65: "#0066FF",
        -55: "#00FF00",
        -40: "#009933"
    }
    

    # Determine the appropriate range for RxLev
    if rxlev <= -105:
        return color_mapping[-105]
    elif -105 < rxlev <= -92:
        return color_mapping[-92]
    elif -92 < rxlev <= -83:
        return color_mapping[-83]
    elif -83 < rxlev <= -76:
        return color_mapping[-76]
    elif -76 < rxlev <= -65:
        return color_mapping[-65]
    elif -65 < rxlev <= -55:
        return color_mapping[-55]
    elif -55 < rxlev <= -40:
        return color_mapping[-40]
    else:
        return "#000000"  # Default color for out-of-range values
    

point_to_layer = assign("""
    function(feature, latlng) {
        if (feature.properties.hidden) {
            return null;  // Do not render hidden features
        }
        return L.circle(latlng, {
            radius: 20,
            color: feature.properties.color,
            fillColor: feature.properties.color,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.5
        });
    }
""")

# for the CS CB
# point_to_layer = assign("""
#     function(feature, latlng) {
#         if (feature.properties.hidden) {
#             return null;  // Skip rendering hidden features
#         }
#         return L.circle(latlng, {
#             radius: 20,
#             color: feature.properties.color,
#             fillColor: feature.properties.color,
#             weight: 1,
#             opacity: 1,
#             fillOpacity: 0.5
#         });
#     }
# """)
style_function = assign("""
    function(feature, context) {
        const {highlighted} = context.hideout;  // Access the highlighted feature
        if (highlighted && feature.properties.id === highlighted) {
            return {weight: 5, color: "black", fillColor: "black"};  // Highlighted style
        }
        return {weight: 1, color: feature.properties.color, fillColor: feature.properties.color};  // Default style
    }
""")
# point_to_layer = assign("""
#     function(feature, latlng) {
#         // Get the current zoom level from the map
#         let zoomLevel = this._map.getZoom();  // 'this' refers to the layer

#         // Calculate dynamic radius (adjust multiplier as needed)
#         let dynamicRadius = 20 * Math.pow(2, (zoomLevel - 10));  // Example formula

#         return L.circle(latlng, {
#             radius: dynamicRadius,  // Dynamic radius based on zoom level
#             color: feature.properties.color,  // Border color
#             fillColor: feature.properties.color,  // Fill color
#             weight: 1,
#             opacity: 1,
#             fillOpacity: 0.5
#         });
#     }
# """)

hover_style = assign("""
    function(feature) {
        return {weight: 3, color: 'white'};
    }
""")

super_cluster_options = assign("""
    function (cluster, points) {
        let totalRxLev = 0;
        let count = points.length;

        // Aggregate RxLev values
        points.forEach(function (point) {
            if (point.properties && point.properties.RxLev !== undefined) {
                totalRxLev += point.properties.RxLev;
            }
        });

        // Calculate average RxLev
        let avgRxLev = totalRxLev / count;

        // Assign the average RxLev to cluster properties
        cluster.properties.avgRxLev = avgRxLev;
        console.log("Cluster properties after reduction:", cluster.properties);
    }
""")


style_handle = assign("""function(feature, context){
    const {selected} = context.hideout;
    if(selected.includes(feature.properties.name)){
        return {fillColor: 'red', color: 'grey'};
    }
    return {fillColor: 'grey', color: 'grey'};
}""")

hover_style = assign("""function(feature, context) {
        return {fillColor: 'yellow', color: 'black'};
    }""")

def get_info(feature=None):
    header = [html.H4("Cell Name")]
    if not feature:
        return header + [html.P("Hover over a Cell")]
    return header + [html.B(feature["properties"]["name"])]

legend_colors = {
    "-105 and below": "#191919",
    "-105 to -92": "#FF0800",
    "-92 to -83": "#FF7300",
    "-83 to -76": "#FFFF00",
    "-76 to -65": "#0066FF",
    "-65 to -55": "#00FF00",
    "-55 to -40": "#009933",
}

# Create the legend as an HTML element
def create_legend():
    return html.Div(
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "5px",
                    "cursor": "pointer"  # Add pointer to indicate interactivity
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
        ],
        style={
            "position": "absolute",
            "top": "10px",  # Adjust for vertical positioning
            "right": "10px",  # Adjust for horizontal positioning
            "padding": "10px",
            "backgroundColor": "white",
            "boxShadow": "0px 0px 5px rgba(0,0,0,0.5)",
            "zIndex": "1000",
            "border": "1px solid black",
            "borderRadius": "5px",
        },
    )