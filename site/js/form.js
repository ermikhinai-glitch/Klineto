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

  /** Fire lead_submit (or other) when Metrika/GA IDs are present — do not invent IDs. */
  function fireGoal(eventName) {
    if (!eventName) return;
    var ymId =
      window.KLINETO_YM_ID ||
      window.YANDEX_METRIKA_ID ||
      (document.querySelector('meta[name="ym:counter"]') &&
        document.querySelector('meta[name="ym:counter"]').getAttribute("content"));
    try {
      if (typeof window.ym === "function" && ymId) {
        window.ym(Number(ymId) || ymId, "reachGoal", eventName);
      }
    } catch (e) {}
    try {
      if (typeof window.gtag === "function") {
        window.gtag("event", eventName);
      }
    } catch (e) {}
    try {
      if (window.dataLayer && typeof window.dataLayer.push === "function") {
        window.dataLayer.push({ event: eventName });
      }
    } catch (e) {}
  }

  function markGoal(form, eventName) {
    form.setAttribute("data-goal-state", eventName || "");
    fireGoal(eventName);
  }

  function phoneOk(value) {
    var phoneDigits = (value.match(/\d/g) || []).length;
    var phoneHasLetters = /[^\d\s()+\-]/.test(value);
    return phoneDigits >= 10 && !phoneHasLetters;
  }

  function bindLeadForm(form) {
    var error = form.querySelector(".form-error");
    var success = form.querySelector(".form-success");
    var nameField =
      form.querySelector("#name") ||
      form.querySelector('[name="name"]') ||
      form.querySelector('input[type="text"]');
    var phoneField =
      form.querySelector("#phone") ||
      form.querySelector('[name="phone"]') ||
      form.querySelector('input[type="tel"]');
    var objectField =
      form.querySelector("#object-type") ||
      form.querySelector('[name="object-type"]');
    var goal = form.getAttribute("data-goal-event") || "lead_submit";

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var required = [nameField, phoneField].filter(Boolean);
      if (objectField) required.push(objectField);

      var missing = required.filter(function (field) {
        var empty = !field.value || field.value.trim() === "";
        field.setAttribute("aria-invalid", empty ? "true" : "false");
        return empty;
      });

      if (missing.length) {
        if (success) {
          success.hidden = true;
        }
        if (error) {
          error.hidden = false;
          error.textContent = objectField
            ? "Заполните имя, телефон и тип объекта."
            : "Заполните имя и телефон.";
        }
        missing[0].focus();
        return;
      }

      if (phoneField && !phoneOk(phoneField.value)) {
        phoneField.setAttribute("aria-invalid", "true");
        if (success) success.hidden = true;
        if (error) {
          error.hidden = false;
          error.textContent = "Проверьте телефон: в номере нужно не меньше 10 цифр.";
        }
        phoneField.focus();
        return;
      }

      if (error) {
        error.hidden = true;
      }
      if (success) {
        success.hidden = false;
        success.textContent = "Заявка принята.";
        success.focus();
      }

      markGoal(form, goal);
      form.reset();
      required.forEach(function (field) {
        field.setAttribute("aria-invalid", "false");
      });
    });
  }

  function bindJobForm(form) {
    var error = form.querySelector(".form-error");
    var success = form.querySelector(".form-success");
    var nameField = form.querySelector('[name="name"]');
    var phoneField = form.querySelector('[name="phone"]');
    var requiredFields = [nameField, phoneField].filter(Boolean);
    var goal = form.getAttribute("data-goal-event") || "lead_submit";

    if (!error || !success || requiredFields.length < 2) {
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
        error.textContent = "Заполните имя и телефон.";
        missing[0].focus();
        return;
      }

      if (!phoneOk(phoneField.value)) {
        phoneField.setAttribute("aria-invalid", "true");
        success.hidden = true;
        error.hidden = false;
        error.textContent = "Проверьте телефон: в номере нужно не меньше 10 цифр.";
        phoneField.focus();
        return;
      }

      error.hidden = true;
      success.hidden = false;
      success.textContent = "Отклик принят.";
      markGoal(form, goal);
      form.reset();
      requiredFields.forEach(function (field) {
        field.setAttribute("aria-invalid", "false");
      });
      success.focus();
    });
  }

  document.querySelectorAll("form.lead-form").forEach(bindLeadForm);
  document.querySelectorAll("form.job-form").forEach(bindJobForm);
})();
