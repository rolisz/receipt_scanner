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
})
var info;
function load_receipts() {
    $.get('/get_receipts', function(data) {
        console.log(data)
        $("#inner_tbl").html(buildTable(data));
        info = data;
        var ctx = $('#myChart');

        var d = {}
        for (var i = 0; i < info.length; i++) {
            if (info[i]["date"] in d) {
				d[info[i]["date"]] += info[i]["total"]; } else {
				d[info[i]["date"]] = info[i]["total"]
                }
        }
        labels = $.map(data, function(e) { return e["date"]})
        data = $.map(data, function(e) { return e["total"]})
        var myBarChart = new Chart(ctx, {
            type: 'bar',
            data: {datasets: [{data: Object.values(d)}], labels: Object.keys(d)},
        });
    })
}