// =====================================================
// static/js/banned-ips.js
// Gestion des IPs bannies
// =====================================================

class BannedIPManager {
  static allBannedIPs = [];

  static async load() {
    try {
      const data = await API.get("/banned-ips");
      this.allBannedIPs = data.banned_ips;
      this.render(this.allBannedIPs);
    } catch (error) {
      console.error("Banned IPs error:", error);
      UI.showEmptyState(
        document.getElementById("bannedIPs"),
        CONFIG.TRANSLATIONS.banned_ips_load_error
      );
    }
  }

  static render(ips) {
    const container = document.getElementById("bannedIPs");

    if (ips.length === 0) {
      UI.showEmptyState(container, CONFIG.TRANSLATIONS.no_banned_ips);
      return;
    }

    container.innerHTML = ips.map((item) => this.renderIPItem(item)).join("");
    UI.refreshIcons();
  }

  static renderIPItem(item) {
    return `
      <div class="ip-item" data-ip="${item.ip}">
        <div class="ip-info">
          <div>
            <div class="ip-address">${item.ip}</div>
            <div class="ip-meta">${item.jail} • ${item.attempts} ${CONFIG.TRANSLATIONS.attempts}</div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn-icon" onclick="BannedIPManager.unban('${item.ip}', '${item.jail}')" title="${CONFIG.TRANSLATIONS.unban}">
            <i data-lucide="unlock" style="width: 18px; height: 18px;"></i>
          </button>
        </div>
      </div>
    `;
  }

  static async unban(ip, jail) {
    if (
      !confirm(
        `${CONFIG.TRANSLATIONS.confirm_unban} ${ip} ${CONFIG.TRANSLATIONS.from_jail} ${jail}?`
      )
    ) {
      return;
    }

    try {
      await API.post("/unban", { ip, jail });
      alert(
        `${CONFIG.TRANSLATIONS.ip_unbanned} ${ip} ${CONFIG.TRANSLATIONS.in_jail} ${jail}!`
      );
      await DataManager.refreshAll();
    } catch (error) {
      console.error("Unban error:", error);
      alert(`${CONFIG.TRANSLATIONS.error}: ${error.message}`);
    }
  }

  static async ban(ip, jail) {
    try {
      await API.post("/ban", { ip, jail });
      alert(
        `${CONFIG.TRANSLATIONS.ip_banned} ${ip} ${CONFIG.TRANSLATIONS.in_jail} ${jail}!`
      );
      await DataManager.refreshAll();
      return true;
    } catch (error) {
      console.error("Ban error:", error);
      alert(`${CONFIG.TRANSLATIONS.error}: ${error.message}`);
      return false;
    }
  }

  static search(query) {
    const filtered = this.allBannedIPs.filter(
      (item) =>
        item.ip.toLowerCase().includes(query) ||
        item.jail.toLowerCase().includes(query)
    );
    this.render(filtered);

    // Suggestion de bannissement
    const container = document.getElementById("banNewIPContainer");
    if (query && !this.allBannedIPs.some((ip) => ip.ip === query)) {
      container.innerHTML = `
        <button class="btn btn-primary" onclick="BannedIPManager.promptBan('${query}')">
          <i data-lucide="lock"></i> ${CONFIG.TRANSLATIONS.ban} ${query}
        </button>
      `;
      UI.refreshIcons();
    } else {
      container.innerHTML = "";
    }
  }

  static async promptBan(ip) {
    const jail = prompt(`${CONFIG.TRANSLATIONS.which_jail} "${ip}"`, "default");
    if (!jail) return;

    const success = await this.ban(ip, jail);
    if (success) {
      document.getElementById("searchIP").value = "";
      document.getElementById("banNewIPContainer").innerHTML = "";
    }
  }
}

// =====================================================
// static/js/modal.js
// Gestion des modales
// =====================================================

class ModalManager {
  static async openJailDetails(jailName) {
    const modal = document.getElementById("jailModal");
    modal.style.display = "flex";
    document.getElementById("modalJailName").textContent = jailName;

    try {
      const data = await API.get("/jails");
      const jail = data.jails.find((j) => j.name === jailName);

      if (jail) {
        document.getElementById("modalJailStatus").textContent = jail.enabled
          ? CONFIG.TRANSLATIONS.active
          : CONFIG.TRANSLATIONS.inactive;
        document.getElementById("modalBannedCount").textContent = jail.banned;
        document.getElementById("modalFailedCount").textContent = jail.failed;
      }

      // Charger les logs
      document.getElementById("modalLogs").textContent =
        CONFIG.TRANSLATIONS.loading_logs;
      const logsData = await API.get(`/logs?jail=${jailName}`);
      document.getElementById("modalLogs").textContent =
        logsData.logs.join("\n") || CONFIG.TRANSLATIONS.no_logs;
    } catch (error) {
      console.error("Modal error:", error);
      document.getElementById("modalLogs").textContent =
        CONFIG.TRANSLATIONS.logs_load_error;
    }
  }

  static closeJailDetails() {
    document.getElementById("jailModal").style.display = "none";
  }

  static openAddJail() {
    document.getElementById("addJailModal").style.display = "flex";
  }

  static closeAddJail() {
    document.getElementById("addJailModal").style.display = "none";
    document.getElementById("addJailForm").reset();
  }

  static updateJailStatus(status) {
    document.getElementById("modalJailStatus").textContent = status;
  }
}
