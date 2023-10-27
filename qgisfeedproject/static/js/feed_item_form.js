// Capture user input in real-time
var titleField = document.getElementById("id_title");
var contentField = document.getElementById("id_content");
var imageField = document.getElementById("id_image");
var urlField = document.getElementById("id_url");
var stickyField = document.getElementById("id_sticky");
var sortingField = document.getElementById("id_sorting");
var languageField = document.getElementById("id_language_filter");
var spatialFilterField = document.getElementById("id_spatial_filter");
var publishFromField = document.getElementById("id_publish_from");
var publishToField = document.getElementById("id_publish_to");

var contentPreview = document.getElementsByName("contentPreview");
var titlePreview = document.getElementsByName("titlePreview");
var imagePreview = document.getElementsByName("imagePreview");
var urlPreview = document.getElementsByName("urlPreview");
var stickyPreview = document.getElementsByName("stickyPreview");
var sortingPreview = document.getElementsByName("sortingPreview");
var languagePreview = document.getElementsByName("languagePreview");
var spatialFilterPreview = document.getElementsByName("spatialFilterPreview");
var publishFromPreview = document.getElementsByName("publishFromPreview");
var publishToPreview = document.getElementsByName("publishToPreview");

var imageFileName = document.getElementById("imageFileName");


// Update title in preview when input change
titleField.addEventListener("input", function () {
  var fieldValue = titleField.value;
  titlePreview.forEach((item) => {
    item.innerText = fieldValue;
  });
});

// Update image in preview when input change
imageField.addEventListener("change", function () {
  var selectedImage = imageField.files[0];
  imagePreview.forEach((item) => {
    if (selectedImage) {
      var imageURL = URL.createObjectURL(selectedImage);
      item.innerHTML =
        '<img src="' + imageURL + '" style="border-radius:20px;">';
      imageFileName.innerHTML = selectedImage.name;
    } else {
      item.innerHTML = "";
      imageFileName.innerHTML =
        "<i>No image chosen. Click here to add an image.</i>";
    }
  });
});

// Update URL in preview when input change
urlField.addEventListener("input", function () {
  urlPreview.forEach((item) => {
    item.innerHTML = urlField.value
      ? '<a href="' +
        urlField.value +
        '" target="_blank">' +
        urlField.value +
        "</a>"
      : "<i>-</i>";
  });
});

// Update sticky in preview when change
stickyField.addEventListener("change", function () {
  stickyPreview.forEach((item) => {
    item.innerHTML = stickyField.checked
    ? '<span class="icon has-text-success">' +
      '<i class="fa-solid fa-circle-check"></i>' +
      "</span>"
    : '<span class="icon has-text-danger">' +
      '<i class="fa-solid fa-circle-xmark"></i>' +
      "</span>";
  });
});

// Update sorting in preview when input change
sortingField.addEventListener("input", function () {
  sortingPreview.forEach((item) => {
    item.innerText = sortingField.value ? sortingField.value : "-";
  });
});

// Update language filter in preview when input change
languageField.addEventListener("change", function () {
  languagePreview.forEach((item) => {
    item.innerText = languageField.value
      // ? languageField.options[languageField.selectedIndex].text
      ? languageField.value
      : "-";
  });
});

// Update spatial filter
function refreshSpatialFilter() {
  spatialFilterPreview.forEach((item) => {
    item.classList.remove("is-success")
    item.classList.remove("is-danger")
    item.classList.add(
      spatialFilterField.value ? "is-success" : "is-danger"
    );
    item.innerText = spatialFilterField.value
      ? "Spatial filter set."
      : "Spatial filter not set.";
  });
}

function refreshDates() {
  publishFromPreview.forEach((item) => {
    item.innerText = publishFromField.value
      ? new Date(publishFromField.value).toString()
      : "-";
  });
  publishToPreview.forEach((item) => {
    item.innerText = publishToField.value
      ? new Date(publishToField.value).toString()
      : "-";
  });
}

// Update publish from in preview when input change
publishFromField.addEventListener("change", function () {
  publishFromPreview.forEach((item) => {
    item.innerText = publishFromField.value
      ? new Date(publishFromField.value).toString()
      : "-";
  });
});

// Update publish to in preview when input change
publishToField.addEventListener("change", function () {
  publishToPreview.forEach((item) => {
    item.innerText = publishToField.value
      ? new Date(publishToField.value).toString()
      : "-";
  });
});


document.addEventListener("DOMContentLoaded", () => {
  // Refresh some fieds on start
  refreshSpatialFilter()
  refreshDates()
  // Functions to open and close the review modal
  function openModal($el) {
    $el.classList.add("is-active");
    refreshSpatialFilter()
  }

  function closeModal($el) {
    $el.classList.remove("is-active");
    refreshSpatialFilter()
  }

  function closeAllModals() {
    (document.querySelectorAll(".modal") || []).forEach(($modal) => {
      closeModal($modal);
      refreshSpatialFilter()
    });
  }

  // Add a click event on buttons to open the modal
  (document.querySelectorAll(".js-modal-trigger") || []).forEach(($trigger) => {
    const modal = $trigger.dataset.target;
    const $target = document.getElementById(modal);

    $trigger.addEventListener("click", () => {
      openModal($target);
    });
  });

  // Add a click event on various child elements to close the parent modal
  (
    document.querySelectorAll(
      ".modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button"
    ) || []
  ).forEach(($close) => {
    const $target = $close.closest(".modal");

    $close.addEventListener("click", () => {
      closeModal($target);
    });
  });

  // Add a keyboard event to close all modals
  document.addEventListener("keydown", (event) => {
    if (event.code === "Escape") {
      closeAllModals();
    }
  });
});
