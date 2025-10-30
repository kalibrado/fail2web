// =====================================================
// static/js/stats.js
// Gestion des statistiques
// =====================================================

class StatsManager {
  static async load() {
    try {
      const data = await API.get('/stats');
      
      document.getElementById('totalBanned').textContent = data.total_banned;
      document.getElementById('activeJails').textContent = data.active_jails;
      document.getElementById('todayBans').textContent = data.total_failed;
      document.getElementById('uptime').textContent = data.uptime;
      document.getElementById('dashboardVersion').textContent = `Dashboard v${data.dashboard_version}`;
      document.getElementById('fail2banVersion').textContent = `Fail2Ban v${data.fail2ban_version}`;
      
      UI.updateStatusBadge(true);
      UI.clearError();
    } catch (error) {
      console.error('Stats error:', error);
      UI.updateStatusBadge(false);
      UI.showError(CONFIG.TRANSLATIONS.stats_load_error || 'Unable to load statistics');
    }
  }
}
