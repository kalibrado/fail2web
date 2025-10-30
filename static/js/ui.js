// =====================================================
// static/js/ui.js
// Gestion de l'interface utilisateur
// =====================================================

class UI {
  static showError(message) {
    const container = document.getElementById('errorContainer');
    container.innerHTML = `
      <div class="error-message">
        <strong>${CONFIG.TRANSLATIONS.error}:</strong> ${message}
      </div>
    `;
  }

  static clearError() {
    document.getElementById('errorContainer').innerHTML = '';
  }

  static updateStatusBadge(isOnline) {
    const badge = document.getElementById('statusBadge');
    if (isOnline) {
      badge.className = 'badge';
      badge.innerHTML = `<div class="loading"></div> ${CONFIG.TRANSLATIONS.service_active}`;
    } else {
      badge.className = 'badge offline';
      badge.innerHTML = `<i data-lucide="x-circle"></i> ${CONFIG.TRANSLATIONS.offline}`;
    }
    lucide.createIcons();
  }

  static setLoading(elementId, isLoading) {
    const element = document.getElementById(elementId);
    if (isLoading) {
      element.disabled = true;
      element.innerHTML = '<div class="loading"></div>';
    } else {
      element.disabled = false;
    }
  }

  static showEmptyState(container, message) {
    container.innerHTML = `<div class="empty-state">${message}</div>`;
  }

  static refreshIcons() {
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }
}
