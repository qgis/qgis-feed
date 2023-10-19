// Capture user input in real-time
var titleField = document.getElementById("id_title");
var contentField = document.getElementById("id_content");
var imageField = document.getElementById("id_image");

var contentPreview = document.getElementById("contentPreview");
var titlePreview = document.getElementById("titlePreview");
var imagePreview = document.getElementById("imagePreview");

var imageFileName = document.getElementById("imageFileName");

titleField.addEventListener("input", function () {
  var fieldValue = titleField.value;
  titlePreview.innerText = fieldValue;
});

contentField.addEventListener("input", function () {
  var fieldValue = contentField.value;
  contentPreview.innerHTML = fieldValue;
});

imageField.addEventListener("change", function () {
  var selectedImage = imageField.files[0];
  if (selectedImage) {
    var imageURL = URL.createObjectURL(selectedImage);
    imagePreview.innerHTML =
      '<img src="' + imageURL + '" style="border-radius:20px;">';
    imageFileName.innerHTML = selectedImage.name;
  } else {
    imagePreview.innerHTML = "";
    imageFileName.innerHTML =
      "<i>No image choosed. Click here to add an image.</i>";
  }
});
