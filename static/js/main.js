// Main JavaScript for Compliance & Recurring Checklist Tracker

document.addEventListener('DOMContentLoaded', function () {
  // 1. Instant Photo Evidence Upload Preview
  const photoInput = document.getElementById('photo_evidence');
  const previewContainer = document.getElementById('photoPreviewContainer');

  if (photoInput && previewContainer) {
    photoInput.addEventListener('change', function () {
      previewContainer.innerHTML = ''; // Clear previous previews
      const files = this.files;

      if (files && files.length > 0) {
        Array.from(files).forEach((file) => {
          if (!file.type.startsWith('image/')) return;

          const reader = new FileReader();
          reader.onload = function (e) {
            const col = document.createElement('div');
            col.className = 'col-auto';

            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'img-thumbnail shadow-sm';
            img.style.width = '100px';
            img.style.height = '100px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '8px';

            col.appendChild(img);
            previewContainer.appendChild(col);
          };
          reader.readAsDataURL(file);
        });
      }
    });
  }

  // 2. Lightbox / Modal for Evidence Inspection
  const evidenceThumbs = document.querySelectorAll('.evidence-thumb');
  const modalImg = document.getElementById('modalImageTarget');
  const imageModalElement = document.getElementById('imageViewerModal');

  if (evidenceThumbs.length > 0 && modalImg && imageModalElement) {
    const modalInstance = new bootstrap.Modal(imageModalElement);
    evidenceThumbs.forEach((thumb) => {
      thumb.addEventListener('click', function () {
        modalImg.src = this.getAttribute('data-full-src');
        modalInstance.show();
      });
    });
  }

  // 3. Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 6000);
  });
});
