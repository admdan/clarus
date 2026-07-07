(function () {
  function getProfileRoot() {
    return document.getElementById("profilePage");
  }

  function getRequestChangeUrl() {
    return getProfileRoot()?.dataset.requestChangeUrl || "";
  }

  function cleanupChangeModalState() {
    const modalElement = document.getElementById("changeModal");
    if (!modalElement) {
      return;
    }

    modalElement.classList.remove("is-open");
    modalElement.setAttribute("aria-hidden", "true");
    document.body.style.removeProperty("overflow");
  }

  function resetChangeRequestModal() {
    const changeField = document.getElementById("changeField");
    const changeNote = document.getElementById("changeNote");
    const inputGroup = document.getElementById("inputGroup");
    const submitButton = document.getElementById("changeRequestSubmit");

    if (changeField) {
      changeField.value = "";
    }
    if (changeNote) {
      changeNote.value = "";
    }
    if (inputGroup) {
      inputGroup.innerHTML = "";
    }
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = "Send Request";
    }
  }

  function buildChangeRequestInput(triggerButton) {
    const field = triggerButton?.dataset.changeField || "";
    const type = triggerButton?.dataset.changeType || "text";
    const options = (triggerButton?.dataset.changeOptions || "")
      .split("|")
      .map((option) => option.trim())
      .filter(Boolean);

    document.getElementById("changeField").value = field;
    document.getElementById("changeNote").value = "";

    const group = document.getElementById("inputGroup");
    group.innerHTML = "";

    const label = document.createElement("label");
    label.className = "form-label";
    label.setAttribute("for", "newValue");
    label.innerText = "Requested Value";
    group.appendChild(label);

    let input;
    if (options.length > 0) {
      input = document.createElement("select");
      input.className = "form-select";

      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.disabled = true;
      placeholder.selected = true;
      placeholder.text = "-- Select a value --";
      input.appendChild(placeholder);

      options.forEach((option) => {
        const choice = document.createElement("option");
        choice.value = option;
        choice.text = option;
        input.appendChild(choice);
      });
    } else if (type === "textarea") {
      input = document.createElement("textarea");
      input.className = "form-control";
      input.rows = 3;
      input.value = "";
    } else {
      input = document.createElement("input");
      input.className = "form-control";
      input.type = type;
      input.value = "";
    }

    input.id = "newValue";
    input.required = true;
    group.appendChild(input);
  }

  function closeChangeRequestModal() {
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    cleanupChangeModalState();
    resetChangeRequestModal();
  }

  function openChangeRequestModal(triggerButton) {
    resetChangeRequestModal();
    buildChangeRequestInput(triggerButton);

    const modalElement = document.getElementById("changeModal");
    cleanupChangeModalState();
    modalElement.classList.add("is-open");
    modalElement.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    const newValueInput = document.getElementById("newValue");
    if (newValueInput) {
      newValueInput.focus();
    }
  }

  function submitChangeRequest(event) {
    event.preventDefault();

    const requestChangeUrl = getRequestChangeUrl();
    const field = document.getElementById("changeField").value;
    const newValueInput = document.getElementById("newValue");

    if (!requestChangeUrl || !newValueInput) {
      alert("Unable to open the change request form correctly. Please try again.");
      return;
    }

    const submitButton = document.getElementById("changeRequestSubmit");
    submitButton.disabled = true;
    submitButton.textContent = "Sending...";

    fetch(requestChangeUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        field,
        new_value: newValueInput.value,
        note: document.getElementById("changeNote").value,
      }),
    })
      .then((response) => {
        if (response.ok) {
          alert("Your update request was submitted for review.");
          closeChangeRequestModal();
          return;
        }

        alert("Unable to submit your update request.");
        submitButton.disabled = false;
        submitButton.textContent = "Send Request";
      })
      .catch(() => {
        alert("Unable to submit your update request.");
        submitButton.disabled = false;
        submitButton.textContent = "Send Request";
      });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const changeModalElement = document.getElementById("changeModal");
    changeModalElement.addEventListener("click", (event) => {
      if (event.target === changeModalElement) {
        closeChangeRequestModal();
      }
    });

    document.body.addEventListener("htmx:beforeSwap", () => {
      if (changeModalElement.classList.contains("is-open")) {
        closeChangeRequestModal();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && changeModalElement.classList.contains("is-open")) {
        closeChangeRequestModal();
      }
    });

    document.getElementById("profileTab").addEventListener("shown.bs.tab", () => {
      if (changeModalElement.classList.contains("is-open")) {
        closeChangeRequestModal();
      } else {
        resetChangeRequestModal();
        cleanupChangeModalState();
      }
    });
  });

  window.openChangeRequestModal = openChangeRequestModal;
  window.closeChangeRequestModal = closeChangeRequestModal;
  window.submitChangeRequest = submitChangeRequest;
})();
