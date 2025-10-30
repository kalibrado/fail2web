// =====================================================
// static/js/config.js
// Configuration et constantes globales
// =====================================================

const CONFIG = {
  API_URL: typeof API_URL !== 'undefined' ? API_URL : window.location.origin + '/api',
  AUTO_REFRESH_INTERVAL: typeof AUTO_REFRESH_INTERVAL !== 'undefined' ? AUTO_REFRESH_INTERVAL : 30000,
  TRANSLATIONS: typeof TRANSLATIONS !== 'undefined' ? TRANSLATIONS : {},
};

