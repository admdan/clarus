(function () {
  function repaintRows() {
    document.querySelectorAll("tr").forEach((row) => {
      row.style.display = "none";
      void row.offsetHeight;
      row.style.display = "";
    });
  }

  function handleThemeChange() {
    repaintRows();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("clarus:theme-changed", handleThemeChange);
  });
})();
