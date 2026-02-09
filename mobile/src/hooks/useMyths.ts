import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getAllMyths } from '../database/queries';
import type { Myth } from '../types/database';

/** Hook que carga todos los mitos. */
export function useMyths() {
  const db = useDatabase();
  const [myths, setMyths] = useState<Myth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getAllMyths(db).then(data => {
      if (mounted) {
        setMyths(data);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, [db]);

  return { myths, loading };
}
