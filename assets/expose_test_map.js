console.log("Expose Test Map Script Loaded");
document.addEventListener("DOMContentLoaded", function () {
    console.log("Expose Test Map Script Loaded");

    const mapElement = document.getElementById("map"); // Adjust ID if your map has a different ID
    if (mapElement) {
        console.log("Map element found:", mapElement);

        const leafletMap = mapElement._leaflet_map; // Access the Leaflet map instance
        if (leafletMap) {
            console.log("Leaflet map instance:", leafletMap);

            // Listen for the layeradd event
            leafletMap.on("layeradd", function (event) {
                console.log("Layer added:", event.layer);

                // Check if this is the test_map GeoJSON layer
                if (event.layer.feature) {
                    console.log("GeoJSON layer detected:", event.layer);

                    // Assign to a global variable
                    window.testMapLayer = event.layer;
                    console.log("GeoJSON layer exposed as testMapLayer:", testMapLayer);
                }
            });
        } else {
            console.error("Leaflet map instance not found.");
        }
    } else {
        console.error("Map element not found.");
    }
});