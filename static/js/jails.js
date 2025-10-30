
// =====================================================
// static/js/jails.js
// Gestion des jails
// =====================================================

class JailManager {
  static async load() {
    try {
      const data = await API.get('/jails');
      const jailList = document.getElementById('jailList');

      if (data.jails.length === 0) {
        UI.showEmptyState(jailList, CONFIG.TRANSLATIONS.no_jails);
        return;
      }

      jailList.innerHTML = data.jails
        .map(jail => this.renderJailItem(jail))
        .join('');

      UI.refreshIcons();
    } catch (error) {
      console.error('Jails error:', error);
      UI.showEmptyState(
        document.getElementById('jailList'),
        CONFIG.TRANSLATIONS.jails_load_error
      );
    }
  }

  static renderJailItem(jail) {
    return `
      <div class="jail-item" data-jail="${jail.name}">
        <div class="jail-header">
          <div class="jail-name">${jail.name}</div>
          <div class="jail-status ${jail.enabled ? 'status-active' : 'status-inactive'}">
            ${jail.enabled ? CONFIG.TRANSLATIONS.active : CONFIG.TRANSLATIONS.inactive}
          </div>
        </div>
        <div class="jail-stats">
          <span><i data-lucide="ban" style="width: 14px; height: 14px;"></i> ${jail.banned} ${CONFIG.TRANSLATIONS.banned_count}</span>
          <span><i data-lucide="alert-circle" style="width: 14px; height: 14px;"></i> ${jail.failed} ${CONFIG.TRANSLATIONS.failed_count}</span>
        </div>
      </div>
    `;
  }

  static async toggle(jailName) {
    try {
      const data = await API.patch(`/jails/${encodeURIComponent(jailName)}/toggle`, {});
      alert(`Jail '${jailName}' ${data.status}`);
      await DataManager.refreshAll();
      ModalManager.updateJailStatus(data.status);
    } catch (error) {
      console.error('Toggle error:', error);
      alert(error.message);
    }
  }

  static async add(jailData) {
    try {
      await API.post('/jails/add', jailData);
      alert(`${CONFIG.TRANSLATIONS.create_jail_success} ${jailData.name}!`);
      ModalManager.closeAddJail();
      await this.load();
      return true;
    } catch (error) {
      console.error('Add jail error:', error);
      alert(`${CONFIG.TRANSLATIONS.jail_creation_error} (${error.message})`);
      return false;
    }
  }
}
