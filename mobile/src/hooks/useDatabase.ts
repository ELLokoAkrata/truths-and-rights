import { useContext } from 'react';
import { DatabaseContext } from '../database/DatabaseProvider';
import type * as SQLite from 'expo-sqlite';

/** Hook que retorna la conexion a la DB. Lanza error si se usa fuera del Provider. */
export function useDatabase(): SQLite.SQLiteDatabase {
  const db = useContext(DatabaseContext);
  if (!db) {
    throw new Error('useDatabase debe usarse dentro de <DatabaseProvider>');
  }
  return db;
}
