import * as FileSystem from 'expo-file-system';
import { Asset } from 'expo-asset';
import * as SQLite from 'expo-sqlite';
import { DB_FILENAME } from '../constants/config';

/**
 * Inicializa la base de datos:
 * 1. Copia el asset DB al documentDirectory si no existe o hay nueva version
 * 2. Abre la conexion
 * 3. Ejecuta PRAGMAs de rendimiento
 */

const DB_DEST = `${FileSystem.documentDirectory}SQLite/${DB_FILENAME}`;

/** Verifica si la DB ya existe en el filesystem. */
async function dbExists(): Promise<boolean> {
  const info = await FileSystem.getInfoAsync(DB_DEST);
  return info.exists;
}

/** Copia la DB desde los assets al filesystem. */
async function copyDbFromAssets(): Promise<void> {
  // Asegurar que el directorio SQLite existe
  const dirInfo = await FileSystem.getInfoAsync(
    `${FileSystem.documentDirectory}SQLite`
  );
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(
      `${FileSystem.documentDirectory}SQLite`,
      { intermediates: true }
    );
  }

  // Cargar el asset
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const asset = Asset.fromModule(require('../../assets/db/truths_and_rights_pe.db'));
  await asset.downloadAsync();

  if (!asset.localUri) {
    throw new Error('No se pudo descargar el asset de la base de datos');
  }

  // Copiar al destino
  await FileSystem.copyAsync({
    from: asset.localUri,
    to: DB_DEST,
  });
}

/** Inicializa y retorna la conexion a la DB. */
export async function initDatabase(): Promise<SQLite.SQLiteDatabase> {
  const exists = await dbExists();

  if (!exists) {
    await copyDbFromAssets();
  }

  const db = await SQLite.openDatabaseAsync(DB_FILENAME);

  // PRAGMAs de rendimiento
  await db.execAsync('PRAGMA journal_mode=WAL');
  await db.execAsync('PRAGMA foreign_keys=ON');

  return db;
}

/**
 * Fuerza la reinstalacion de la DB (cuando hay nueva version).
 * Elimina la existente y copia la nueva.
 */
export async function reinstallDatabase(): Promise<SQLite.SQLiteDatabase> {
  const exists = await dbExists();
  if (exists) {
    await FileSystem.deleteAsync(DB_DEST, { idempotent: true });
  }
  await copyDbFromAssets();

  const db = await SQLite.openDatabaseAsync(DB_FILENAME);
  await db.execAsync('PRAGMA journal_mode=WAL');
  await db.execAsync('PRAGMA foreign_keys=ON');

  return db;
}
