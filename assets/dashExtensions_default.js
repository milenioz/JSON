window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
                if (feature.properties.hidden) {
                    return null; // Do not render hidden features
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

            ,
        function1: function(feature, context) {
                const {
                    highlighted
                } = context.hideout; // Access the highlighted feature
                if (highlighted && feature.properties.id === highlighted) {
                    return {
                        weight: 5,
                        color: "black",
                        fillColor: "black"
                    }; // Highlighted style
                }
                return {
                    weight: 1,
                    color: feature.properties.color,
                    fillColor: feature.properties.color
                }; // Default style
            }

            ,
        function2: function(feature) {
                return {
                    weight: 3,
                    color: 'white'
                };
            }

            ,
        function3: function(cluster, points) {
                let totalRxLev = 0;
                let count = points.length;

                // Aggregate RxLev values
                points.forEach(function(point) {
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

            ,
        function4: function(feature, context) {
            const {
                selected
            } = context.hideout;
            if (selected.includes(feature.properties.name)) {
                return {
                    fillColor: 'red',
                    color: 'grey'
                };
            }
            return {
                fillColor: 'grey',
                color: 'grey'
            };
        },
        function5: function(feature, context) {
            return {
                fillColor: 'yellow',
                color: 'black'
            };
        }
    }
});