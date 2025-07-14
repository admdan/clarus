document.addEventListener('DOMContentLoaded', () => {

  // ==============================
  // 🟦 AUTH UI: Login/Register Switch
  // ==============================
  const container = document.querySelector('.container');
  const registerBtn = document.querySelector('.register-btn');
  const loginBtn = document.querySelector('.login-btn');

  if (container && registerBtn && loginBtn) {
    registerBtn.addEventListener('click', () => {
      container.classList.add('active');
    });

    loginBtn.addEventListener('click', () => {
      container.classList.remove('active');
    });
  }

  // ==============================
  // 🟩 PROFILE: Document Upload Preview
  // ==============================
  const fileInput = document.querySelector('input[name="document"]');

  if (fileInput) {
    const previewContainer = document.createElement('div');
    previewContainer.id = "doc-preview";
    previewContainer.className = "mt-3";
    fileInput.closest('form').appendChild(previewContainer);

    fileInput.addEventListener('change', function () {
      const file = this.files[0];
      const preview = document.getElementById('doc-preview');
      preview.innerHTML = ''; // Clear previous preview

      if (!file) return;

      const fileType = file.type;

      if (fileType.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = '100%';
        img.style.maxHeight = '300px';
        img.onload = () => URL.revokeObjectURL(img.src);
        preview.appendChild(img);
      } else if (fileType === 'application/pdf') {
        const iframe = document.createElement('iframe');
        iframe.src = URL.createObjectURL(file);
        iframe.width = "100%";
        iframe.height = "400px";
        iframe.onload = () => URL.revokeObjectURL(iframe.src);
        preview.appendChild(iframe);
      } else {
        preview.textContent = "Preview not available for this file type.";
      }
    });
  }

  // ==============================
  // 🟨 Additional Modules (Future)
  // ==============================
  // Add future HTMX, modals, UI feedback, etc.

});
