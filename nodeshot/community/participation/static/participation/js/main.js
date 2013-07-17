

//Map initialization
var map = L.map('map').setView([41.87, 12.49], 9);
var osm_layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
//Uncomment for Google maps. Works only in quirk mode.
var ggl_hybrid = new L.Google('HYBRID');
var ggl_map = new L.Google('ROADMAP');
var ggl_sat = new L.Google();

//OSM layer added to map
osm_layer.addTo(map);
map.on('click', onMapClick);
var popup = L.popup();
//Layer insert
var overlaymaps={};
layers= getData('http://localhost:8000/api/v1/layers/');
console.log(layers);
load_layers(layers);




//var pisa = new L.MarkerClusterGroup();
//pisa_nodes=   getData('http://localhost:8000/api/v1/layers/pisa/geojson/');
//pisa_nodes_layer=load_nodes(pisa_nodes)	;
//pisa.addLayer(pisa_nodes_layer);
//map.addLayer(pisa); 
		 
var baseMaps = {
		"OpenStreetMap": osm_layer,
		//Uncomment for Google maps. Works only in quirk mode.
		"Google Sat": ggl_sat,
		"Google Map": ggl_map,
		"Google Hybrid": ggl_hybrid
		
				};
				
//var overlaymaps = {
//			
//			
//			"Roma": roma,
//			"Pisa" : pisa,
//		};

L.control.layers(baseMaps,overlaymaps).addTo(map);

