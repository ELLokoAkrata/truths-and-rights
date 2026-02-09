import { useEffect, useState } from 'react';
import { STATUS_JSON_URL, DB_VERSION, UPDATE_CHECK_INTERVAL } from '../constants/config';
import { useAppStore } from '../store/useAppStore';

/**
 * Hook que verifica si hay una actualizacion de datos disponible.
 * Solo notifica en v0.4.0 — no descarga automaticamente.
 */
export function useDataUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const lastCheck = useAppStore(s => s.lastUpdateCheck);
  const setLastCheck = useAppStore(s => s.setLastUpdateCheck);

  useEffect(() => {
    // No verificar si ya se verifico recientemente
    if (lastCheck && Date.now() - lastCheck < UPDATE_CHECK_INTERVAL) {
      return;
    }

    let mounted = true;

    async function checkUpdate() {
      try {
        const response = await fetch(STATUS_JSON_URL);
        if (!response.ok) return;

        const data = await response.json();
        const remoteDate = data?.generated_at;

        if (remoteDate && remoteDate > DB_VERSION) {
          if (mounted) setUpdateAvailable(true);
        }

        if (mounted) setLastCheck(Date.now());
      } catch {
        // Sin internet o error de red — ignorar silenciosamente
      }
    }

    checkUpdate();

    return () => { mounted = false; };
  }, [lastCheck, setLastCheck]);

  return { updateAvailable };
}
