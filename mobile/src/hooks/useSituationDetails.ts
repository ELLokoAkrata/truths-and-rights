import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getSituationDetails, getSituation } from '../database/queries';
import type { Situation, SituationDetails } from '../types/database';

/** Hook que carga todos los detalles de una situacion en paralelo. */
export function useSituationDetails(situationId: string) {
  const db = useDatabase();
  const [situation, setSituation] = useState<Situation | null>(null);
  const [details, setDetails] = useState<SituationDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    Promise.all([
      getSituation(db, situationId),
      getSituationDetails(db, situationId),
    ]).then(([sit, det]) => {
      if (mounted) {
        setSituation(sit);
        setDetails(det);
        setLoading(false);
      }
    });

    return () => { mounted = false; };
  }, [db, situationId]);

  return { situation, details, loading };
}
