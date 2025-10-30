
// =====================================================
// static/js/data-manager.js
// Orchestrateur de chargement des données
// =====================================================

class DataManager {
  static async refreshAll() {
    const btn = document.getElementById('refreshBtn');
    if (btn) btn.disabled = true;

    await Promise.all([
      StatsManager.load(),
      JailManager.load(),
      BannedIPManager.load()
    ]);

    if (btn) btn.disabled = false;
  }

  static startAutoRefresh() {
    setInterval(() => this.refreshAll(), CONFIG.AUTO_REFRESH_INTERVAL);
  }
}
