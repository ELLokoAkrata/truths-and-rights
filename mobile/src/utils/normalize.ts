/**
 * Normalizacion de texto — port de scripts/search.py normalize().
 * Minusculas, sin tildes, sin puntuacion.
 */

/** Elimina diacriticos (tildes, dieresis, etc.) */
function removeDiacritics(text: string): string {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

/** Normaliza texto: minusculas, sin tildes, sin puntuacion, espacios colapsados. */
export function normalize(text: string): string {
  let result = text.toLowerCase().trim();
  result = removeDiacritics(result);
  result = result.replace(/[^\w\s]/g, '');
  result = result.replace(/\s+/g, ' ');
  return result;
}

/** Divide texto normalizado en tokens unicos. */
export function tokenize(text: string): Set<string> {
  return new Set(normalize(text).split(' ').filter(Boolean));
}

/** Stopwords en espanol — no aportan al matching. */
export const STOPWORDS = new Set([
  'me', 'mi', 'yo', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
  'de', 'del', 'en', 'a', 'al', 'por', 'para', 'con', 'sin', 'que', 'es',
  'y', 'o', 'no', 'si', 'se', 'lo', 'le', 'les', 'su', 'sus', 'como',
  'pero', 'mas', 'muy', 'ya', 'esta', 'esto', 'ese', 'esa', 'esos', 'esas',
  'hay', 'han', 'ha', 'he', 'ser', 'son', 'fue', 'van', 'ir', 'te', 'tu',
  'nos', 'cuando', 'donde', 'quien', 'cual', 'cuanto',
]);

/** Tokeniza y filtra stopwords. */
export function tokensSinStopwords(text: string): Set<string> {
  const tokens = tokenize(text);
  const filtered = new Set<string>();
  for (const t of tokens) {
    if (!STOPWORDS.has(t)) {
      filtered.add(t);
    }
  }
  return filtered;
}
