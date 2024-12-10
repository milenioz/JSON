window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.my_filtering = {
    updateGeoJSON: function(selectedColors, nClicks, geojsonData, bounds) {
        console.log("Selected Colors:", selectedColors); // Debug
        console.log("GeoJSON Data:", geojsonData);       // Debug
        console.log("Bounds:", bounds);                 // Debug

        if (!geojsonData || !geojsonData.features) {
            console.log("GeoJSON data is empty or invalid.");
            return geojsonData;  // Return as-is if no valid data
        }

        // Filter features based on selected colors
        geojsonData.features.forEach(function(feature) {
            feature.properties.hidden = !selectedColors.includes(feature.properties.color);
        });

        return geojsonData;
    }
};

// window.dash_clientside = window.dash_clientside || {};
// window.dash_clientside.my_filtering = {
//     test: function(a, b) {
//         console.log("Test function triggered with args:", a, b);
//         return a + b;
//     }
// };