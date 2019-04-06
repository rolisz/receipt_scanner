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
                    "qty": {
                        type: "string",
                        title: "Item Quantiy"
                    },
                    "unit_price": {
                        type: "number",
                        title: "Unit price"
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
            })
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
                $.post("/upload", {
                    "image": event.target.result
                }, showResults);

            };
            reader.readAsDataURL(v);
        })
	})


})