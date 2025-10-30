// =====================================================
// static/js/app.js
// Point d'entrée principal
// =====================================================

class App {
  static async init() {
    console.log("🚀 Fail2ban Dashboard initializing...");

    // Initialiser les icônes Lucide
    UI.refreshIcons();

    // Charger les données initiales
    await DataManager.refreshAll();

    // Initialiser les événements
    EventHandlers.init();

    // Démarrer l'auto-refresh
    DataManager.startAutoRefresh();

    console.log("✅ Dashboard ready!");
  }
}

// Initialisation au chargement du DOM
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
