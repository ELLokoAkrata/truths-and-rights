import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getAllRights } from '../database/queries';
import type { Right } from '../types/database';

/** Hook que carga todos los derechos. */
export function useRights() {
  const db = useDatabase();
  const [rights, setRights] = useState<Right[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getAllRights(db).then(data => {
      if (mounted) {
        setRights(data);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, [db]);

  return { rights, loading };
}
