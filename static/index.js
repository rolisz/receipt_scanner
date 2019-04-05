// Set constraints for the video stream
var constraints = { video: { facingMode: "user" }, audio: false };
var track = null;
var imageCapture = null;

// Define constants
const cameraView = document.querySelector("#camera--view"),
    cameraOutput = $("#camera--output"),
    cameraTrigger = document.querySelector("#camera--trigger");

// Access the device camera and stream to cameraView
function cameraStart() {
    navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function(stream) {
            track = stream.getVideoTracks()[0];
            imageCapture = new ImageCapture(track);
            console.log(imageCapture);

            cameraView.srcObject = stream;
        })
        .catch(function(error) {
            console.error("Oops. Something is broken.", error);
        });
}
function error(error)
{
    console.error('error:', error);
}
// Take a picture when cameraTrigger is tapped
cameraTrigger.onclick = function() {
    imageCapture.takePhoto()
        .then(blob => {
            var reader = new FileReader();
            reader.onload = function(event){
                var img = $("<div class='camera_image'><img class='taken'/><div class='remove'>X</div></div>")
                img.children('img').attr('src', event.target.result)
                cameraOutput.append(img)
                img.children('.remove').on('click', function(self) {
                    $(this).parent().remove()
                })
                $.post("/upload", {
                    "image": event.target.result
                }, function( data) {
                    console.log(data)
                    $('form').jsonForm({
                        schema: {
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
                        },
                        onSubmit: function (errors, values) {
                          if (errors) {
                            $('#res').html('<p>I beg your pardon?</p>');
                          }
                          else {
                            $('#res').html('<p>Hello ' + values.name + '.' +
                              (values.age ? '<br/>You are ' + values.age + '.' : '') +
                              '</p>');
                          }
                        },
                        value: data
                      });

                });
                }
            reader.readAsDataURL(blob);//Convert the blob from clipboard to base64


        })
        .catch(error);
};

// Start the video stream when the window loads
window.addEventListener("load", cameraStart, false);

$(function() {

})