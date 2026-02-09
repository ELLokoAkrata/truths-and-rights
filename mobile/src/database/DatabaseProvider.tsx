import React, { createContext, useEffect, useState, ReactNode } from 'react';
import * as SplashScreen from 'expo-splash-screen';
import * as SQLite from 'expo-sqlite';
import { initDatabase } from './initDatabase';

/** Contexto que expone la conexion a la DB. */
export const DatabaseContext = createContext<SQLite.SQLiteDatabase | null>(null);

// Evitar que el splash se oculte automaticamente
SplashScreen.preventAutoHideAsync();

interface Props {
  children: ReactNode;
}

export function DatabaseProvider({ children }: Props) {
  const [db, setDb] = useState<SQLite.SQLiteDatabase | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function init() {
      try {
        const database = await initDatabase();
        if (mounted) {
          setDb(database);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Error al inicializar la base de datos');
        }
      } finally {
        // Ocultar splash una vez cargada la DB (o si hay error)
        await SplashScreen.hideAsync();
      }
    }

    init();

    return () => {
      mounted = false;
    };
  }, []);

  if (error) {
    // Renderizar error minimo — en produccion se mostraria una pantalla de error
    return null;
  }

  if (!db) {
    // Aun cargando — splash visible
    return null;
  }

  return (
    <DatabaseContext.Provider value={db}>
      {children}
    </DatabaseContext.Provider>
  );
}
