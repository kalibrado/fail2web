// =====================================================
// static/js/events.js
// Gestion des événements
// =====================================================

class EventHandlers {
  static init() {
    // Recherche d'IP
    document
      .getElementById("searchIP")
      ?.addEventListener("input", function (e) {
        const query = e.target.value.toLowerCase();
        BannedIPManager.search(query);
      });

    // Click sur une jail
    document.addEventListener("click", function (e) {
      const jailItem = e.target.closest(".jail-item");
      if (jailItem) {
        const jailName = jailItem.querySelector(".jail-name").textContent;
        ModalManager.openJailDetails(jailName);
      }
    });

    // Boutons modales
    document.getElementById("addJailBtn")?.addEventListener("click", () => {
      ModalManager.openAddJail();
    });

    document.getElementById("closeAddJail")?.addEventListener("click", () => {
      ModalManager.closeAddJail();
    });

    document.getElementById("jailModalBtn")?.addEventListener("click", () => {
      ModalManager.closeJailDetails();
    });

    // Click en dehors de la modale
    window.addEventListener("click", (e) => {
      const addJailModal = document.getElementById("addJailModal");
      if (e.target === addJailModal) {
        ModalManager.closeAddJail();
      }
    });

    // Formulaire d'ajout de jail
    document
      .getElementById("addJailForm")
      ?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const jailData = {
          name: document.getElementById("jailName").value.trim(),
          filter: document.getElementById("jailFilter").value.trim(),
          port: document.getElementById("jailPort").value.trim(),
          maxretry: parseInt(document.getElementById("jailMaxRetry").value, 10),
          bantime: parseInt(document.getElementById("jailBanTime").value, 10),
        };

        await JailManager.add(jailData);
      });

    // Toggle jail
    document.getElementById("toggleJailBtn")?.addEventListener("click", () => {
      const jailName = document
        .getElementById("modalJailName")
        .textContent.trim();
      JailManager.toggle(jailName);
    });

    // Bouton refresh
    document.getElementById("refreshBtn")?.addEventListener("click", () => {
      DataManager.refreshAll();
    });
  }
}
