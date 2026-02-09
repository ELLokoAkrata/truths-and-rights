#!/usr/bin/env node
/**
 * Copia la base de datos generada por build_db.py a los assets de la app movil.
 *
 * Uso:
 *   node scripts/copy-db.js
 *   npm run copy-db
 */

const fs = require('fs');
const path = require('path');

const SOURCE = path.resolve(__dirname, '..', '..', 'build', 'truths_and_rights_pe.db');
const DEST_DIR = path.resolve(__dirname, '..', 'assets', 'db');
const DEST = path.join(DEST_DIR, 'truths_and_rights_pe.db');

if (!fs.existsSync(SOURCE)) {
  console.error(`ERROR: No se encontro la base de datos: ${SOURCE}`);
  console.error('Ejecuta primero: make build-pe (o python scripts/build_db.py --country PE)');
  process.exit(1);
}

if (!fs.existsSync(DEST_DIR)) {
  fs.mkdirSync(DEST_DIR, { recursive: true });
}

fs.copyFileSync(SOURCE, DEST);

const stats = fs.statSync(DEST);
const sizeKB = Math.round(stats.size / 1024);
console.log(`DB copiada: ${DEST} (${sizeKB} KB)`);
