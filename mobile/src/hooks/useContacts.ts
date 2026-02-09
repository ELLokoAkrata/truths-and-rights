import { useEffect, useState } from 'react';
import { useDatabase } from './useDatabase';
import { getAllContacts } from '../database/queries';
import type { EmergencyContact } from '../types/database';

/** Hook que carga todos los contactos de emergencia. */
export function useContacts() {
  const db = useDatabase();
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getAllContacts(db).then(data => {
      if (mounted) {
        setContacts(data);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, [db]);

  return { contacts, loading };
}
