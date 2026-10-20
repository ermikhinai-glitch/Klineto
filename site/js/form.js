(function () {
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    function setOpen(open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Закрыть меню" : "Меню");
      document.body.classList.toggle("nav-open", open);
    }

    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      setOpen(open);
      if (open) {
        requestAnimationFrame(function () {
          var first = nav.querySelector("a");
          if (first) first.focus();
        });
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        setOpen(false);
      }
    });
  }

  function bindLeadForm(form) {
    var error = form.querySelector(".form-error");
    var success = form.querySelector(".form-success");
    var nameField = form.querySelector("#name") || form.querySelector('[name="name"]');
    var phoneField = form.querySelector("#phone") || form.querySelector('[name="phone"]');
    var objectField = form.querySelector("#object-type") || form.querySelector('[name="object-type"]');
    var requiredFields = [nameField, phoneField, objectField].filter(Boolean);

    if (!error || !success || requiredFields.length < 3) {
      return;
    }

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

      var phoneDigits = (phoneField.value.match(/\d/g) || []).length;
      var phoneHasLetters = /[^\d\s()+\-]/.test(phoneField.value);
      if (phoneDigits < 10 || phoneHasLetters) {
        phoneField.setAttribute("aria-invalid", "true");
        success.hidden = true;
        error.hidden = false;
        error.textContent = "Проверьте телефон: в номере нужно не меньше 10 цифр.";
        phoneField.focus();
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
  }

  document.querySelectorAll("form.lead-form").forEach(bindLeadForm);
})();
