var schema = {
          "id": {
            type: 'number',
            title: 'ID'
          },
          "company": {
            type: 'string',
            title: 'Company',
          },
          "address": {
            type: 'string',
            title: 'Address'
          },
          "items": {
            type: 'array',
            title: 'Items',
            items: {
                type: "object",
                title: "Item",
                properties: {
                    "name": {
                        type: "string",
                        title: "Item Name"
                    },
                    "price": {
                        type: "number",
                        title: "Item price"
                    }
                }
            }
          },
          "total": {
            type: 'number',
            title: 'Total'
          },
          "date": {
            type: 'datetime',
            title: 'Date'
          }
        }
function error(error)
{
    console.error('error:', error);
}

function showResults(data) {
    console.log(data)
    $('#results').empty()
    $(document.createElement('form')).appendTo($('#results'))
        .addClass('panel').jsonForm({
        schema: schema,
//        form:  [
//            {
//              "key": "id",
//              "type": "hidden"
//            },
//            "*",
//            ],
        onSubmit: function (errors, values) {
            console.log(values)
            $.post('/save', {
                values
            });
            $('#results').empty();
            load_receipts();
        },
        value: data
    })
}
 var platform, targetElement, defaultLayers, map, behavior, ui;
$(function() {
	$("#capture").on('change', function(e) {
        var input = e.target;
        $.each(input.files, function(i, v) {
            var reader = new FileReader();
            reader.onload = function(event) {
                var img = $("<div class='camera_image'><img class='taken'/><div class='remove'>X</div></div>")
                img.children('img').attr('src', event.target.result)
                $('#cameraOutput').append(img)
                img.children('.remove').on('click', function(self) {
                    $(this).parent().remove()
                })
                img.on('click', function() {
                    showResults($(this).data("values"))
                })
                $.post("/upload", {
                    "image": event.target.result
                }, function(data) {
                    console.log(data)
                    console.log(img)
                    img.data("values", data);
                    showResults(data)
                });

            };
            reader.readAsDataURL(v);
        })
	})

    load_receipts()
      // Instantiate a map and platform object:
         platform = new H.service.Platform({
          'app_id': '92J6wAWhoND0ytbkEIWE',
          'app_code': 'J2fAUxEbn04RCKVkMl-WpA'
        });
        // Retrieve the target element for the map:
         targetElement = document.getElementById('mapContainer');

        // Get default map types from the platform object:
         defaultLayers = platform.createDefaultLayers();

        // Instantiate the map:
         map = new H.Map(
          document.getElementById('mapContainer'),
          defaultLayers.normal.map,
          {
          zoom: 10,
          center: { lat: 47.046018, lng:21.91039452 }
          });
        //Step 3: make the map interactive
        // MapEvents enables the event system
        // Behavior implements default interactions for pan/zoom (also on mobile touch environments)
         behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

        // Create the default UI components
         ui = H.ui.UI.createDefault(map, defaultLayers);

})
var info;



function load_receipts() {
    $.get('/get_receipts', function(json_data) {
        console.log(json_data)
        $("#inner_tbl").html(buildTable(json_data));
        info = json_data;
        var ctx = $('#myChart');

        var d = {}
        for (var i = 0; i < json_data.length; i++) {
            if (info[i]["date"] in d) {
				d[info[i]["date"]] += info[i]["total"]; } else {
				d[info[i]["date"]] = info[i]["total"]
                }
        }
        labels = $.map(json_data, function(e) { return e["date"]})
        data = $.map(json_data, function(e) { return e["total"]})
        var myBarChart = new Chart(ctx, {
            type: 'bar',
            data: {datasets: [{data: Object.values(d)}], labels: Object.keys(d)},
        });



        // Create the parameters for the geocoding request:

        // Define a callback function to process the geocoding response:
        var onResult = function(result) {
          var locations = result.Response.View[0].Result,
            position,
            marker;
          // Add a marker for each location found
          for (i = 0;  i < locations.length; i++) {
          position = {
            lat: locations[i].Location.DisplayPosition.Latitude,
            lng: locations[i].Location.DisplayPosition.Longitude
          };
          marker = new H.map.Marker(position);
          map.addObject(marker);

          }
          map.setCenter({lat:locations[0].Location.DisplayPosition.Latitude,
                        lng:locations[0].Location.DisplayPosition.Longitude});
          map.setZoom(14);
        };

        // Get an instance of the geocoding service:
        var geocoder = platform.getGeocodingService();

         for (var i = 0; i < json_data.length; i++) {
            var geocodingParams = {
              searchText: json_data[i]["address"]
            };
            console.log(json_data[i], geocodingParams)
            // Call the geocode method with the geocoding parameters,
            // the callback and an error callback function (called if a
            // communication error occurs):
            geocoder.geocode(geocodingParams, onResult, function(e) {
              alert(e);
            });
        }



    })
}