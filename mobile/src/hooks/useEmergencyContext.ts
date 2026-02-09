import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getActiveEmergencyContext } from '../database/queries';
import type { Context } from '../types/database';

/**
 * Hook que determina si hay un estado de emergencia activo.
 * Verifica la fecha del dispositivo contra end_date del decreto.
 */
export function useEmergencyContext() {
  const db = useDatabase();
  const [context, setContext] = useState<Context | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    getActiveEmergencyContext(db).then(ctx => {
      if (!mounted) return;

      if (ctx && ctx.end_date) {
        // Verificar vigencia local
        const now = new Date();
        const end = new Date(ctx.end_date + 'T23:59:59');
        const active = now <= end;
        setContext(ctx);
        setIsActive(active);
      } else if (ctx) {
        // Activo sin fecha de fin
        setContext(ctx);
        setIsActive(true);
      } else {
        setContext(null);
        setIsActive(false);
      }
      setLoading(false);
    });

    return () => { mounted = false; };
  }, [db]);

  return { context, isActive, loading };
}
