/**
 * Configuracion global de la app.
 */

/** Version de la DB embebida. Se compara con status.json remoto. */
export const DB_VERSION = '2026-02-08';

/** URL del status.json del portal publico. */
export const STATUS_JSON_URL =
  'https://ellokoakrata.github.io/truths-and-rights/status.json';

/** Nombre del archivo de la DB. */
export const DB_FILENAME = 'truths_and_rights_pe.db';

/** Codigo de pais activo. */
export const COUNTRY_CODE = 'PE';

/** Version de la app. */
export const APP_VERSION = '0.4.0';

/** Intervalo minimo entre checks de actualizacion (ms). 24 horas. */
export const UPDATE_CHECK_INTERVAL = 24 * 60 * 60 * 1000;
