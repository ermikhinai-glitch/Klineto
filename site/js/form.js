(function () {
  var form = document.querySelector(".lead-form");
  if (!form) {
    return;
  }

  var error = form.querySelector(".form-error");
  var success = form.querySelector(".form-success");
  var requiredFields = [
    form.querySelector("#name"),
    form.querySelector("#phone"),
    form.querySelector("#object-type")
  ];

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var missing = requiredFields.filter(function (field) {
      var empty = field.value.trim() === "";
      field.setAttribute("aria-invalid", empty ? "true" : "false");
      return empty;
    });

    if (missing.length) {
      success.hidden = true;
      error.hidden = false;
      error.textContent = "Заполните имя, телефон и тип объекта.";
      missing[0].focus();
      return;
    }

    error.hidden = true;
    success.hidden = false;
    success.textContent = "Заявка принята.";
    form.setAttribute("data-goal-state", form.getAttribute("data-goal-event") || "");
    form.reset();
    requiredFields.forEach(function (field) {
      field.setAttribute("aria-invalid", "false");
    });
    success.focus();
  });
})();
