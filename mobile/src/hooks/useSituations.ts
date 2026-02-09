import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getAllSituations } from '../database/queries';
import type { Situation } from '../types/database';

/** Hook que carga todas las situaciones activas. */
export function useSituations() {
  const db = useDatabase();
  const [situations, setSituations] = useState<Situation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getAllSituations(db).then(data => {
      if (mounted) {
        setSituations(data);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, [db]);

  return { situations, loading };
}
