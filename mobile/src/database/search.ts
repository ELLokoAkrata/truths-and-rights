import * as SQLite from 'expo-sqlite';
import { normalize, tokenize, tokensSinStopwords } from '../utils/normalize';
import type { SearchResult } from '../types/database';

/**
 * Motor de busqueda — port directo de scripts/search.py.
 * Misma logica: score multicriterio con pesos:
 *   natural_queries (45%) + keywords (30%) + title (15%) + partial (10%)
 *
 * Con 9 situaciones la busqueda en memoria es <5ms, no necesita FTS5.
 */

/** Puntaje por coincidencia con keywords de la situacion. */
function scoreKeywordMatch(queryTokens: Set<string>, keywordsStr: string): number {
  const kwTokens = tokenize(keywordsStr);
  const matches = new Set([...queryTokens].filter(t => kwTokens.has(t)));
  if (matches.size === 0) return 0;
  return matches.size / kwTokens.size;
}

/** Puntaje por similitud con natural_queries de la situacion. */
function scoreNaturalQueryMatch(queryNorm: string, naturalQueriesStr: string): number {
  const queries = naturalQueriesStr.split('|');
  let best = 0;

  for (const nq of queries) {
    const nqNorm = normalize(nq);

    // Match exacto o contenido
    if (queryNorm === nqNorm) return 1.0;
    if (queryNorm.includes(nqNorm) || nqNorm.includes(queryNorm)) {
      const ratio = Math.min(queryNorm.length, nqNorm.length) /
                    Math.max(queryNorm.length, nqNorm.length);
      best = Math.max(best, 0.7 + 0.3 * ratio);
      continue;
    }

    // Match por tokens compartidos
    const qTokens = tokensSinStopwords(queryNorm);
    const nqTokens = tokensSinStopwords(nqNorm);

    if (qTokens.size === 0 || nqTokens.size === 0) continue;

    const shared = new Set([...qTokens].filter(t => nqTokens.has(t)));
    if (shared.size > 0) {
      const precision = shared.size / qTokens.size;
      const recall = shared.size / nqTokens.size;
      if (precision + recall > 0) {
        const f1 = 2 * precision * recall / (precision + recall);
        best = Math.max(best, f1 * 0.8);
      }
    }
  }

  return best;
}

/** Puntaje por similitud con el titulo de la situacion. */
function scoreTitleMatch(queryNorm: string, title: string): number {
  const titleNorm = normalize(title);
  const qTokens = tokensSinStopwords(queryNorm);
  const tTokens = tokensSinStopwords(titleNorm);

  if (qTokens.size === 0 || tTokens.size === 0) return 0;

  const shared = new Set([...qTokens].filter(t => tTokens.has(t)));
  if (shared.size > 0) {
    return shared.size / Math.max(qTokens.size, tTokens.size) * 0.5;
  }
  return 0;
}

/** Puntaje por coincidencia parcial (prefijos de 4+ caracteres). */
function scorePartialMatch(queryTokens: Set<string>, targetStr: string): number {
  const targetTokens = tokenize(targetStr);
  let score = 0;

  for (const qt of queryTokens) {
    if (qt.length < 4) continue;
    for (const tt of targetTokens) {
      if (tt.length < 4) continue;
      // Prefijo comun
      const prefix = qt.substring(0, 4);
      if (tt.startsWith(prefix)) {
        let overlap = 0;
        const minLen = Math.min(qt.length, tt.length);
        for (let i = 0; i < minLen; i++) {
          if (qt[i] === tt[i]) {
            overlap++;
          } else {
            break;
          }
        }
        const ratio = overlap / Math.max(qt.length, tt.length);
        score = Math.max(score, ratio * 0.4);
      }
    }
  }

  return score;
}

/** Cache de situaciones para busquedas repetidas. */
interface SituationRow {
  id: string;
  title: string;
  description: string;
  keywords: string;
  natural_queries: string;
  severity: string;
  category: string;
}

let cachedSituations: SituationRow[] | null = null;

/**
 * Busca la situacion mas relevante para una consulta en lenguaje natural.
 * Port directo de search_situation() de scripts/search.py.
 */
export async function searchSituation(
  db: SQLite.SQLiteDatabase,
  query: string,
  limit: number = 3
): Promise<SearchResult[]> {
  const queryNorm = normalize(query);
  if (!queryNorm) return [];

  const queryTokens = tokensSinStopwords(query);

  // Cargar situaciones (con cache en memoria)
  if (!cachedSituations) {
    cachedSituations = await db.getAllAsync<SituationRow>(
      `SELECT id, title, description, keywords, natural_queries, severity, category
       FROM situations
       WHERE is_active = 1`
    );
  }

  const results: SearchResult[] = [];

  for (const row of cachedSituations) {
    const keywords = row.keywords || '';
    const naturalQ = row.natural_queries || '';
    const title = row.title || '';

    // Calcular puntajes parciales
    const kwScore = scoreKeywordMatch(queryTokens, keywords);
    const nqScore = scoreNaturalQueryMatch(queryNorm, naturalQ);
    const titleScore = scoreTitleMatch(queryNorm, title);
    const partialScore = scorePartialMatch(queryTokens, keywords + ' ' + naturalQ);

    // Puntaje final ponderado
    const total = (nqScore * 0.45) + (kwScore * 0.30) + (titleScore * 0.15) + (partialScore * 0.10);

    if (total > 0.05) {
      results.push({
        situation_id: row.id,
        title: row.title,
        description: row.description,
        severity: row.severity,
        category: row.category,
        score: Math.round(total * 10000) / 10000,
        match_details: {
          natural_query: Math.round(nqScore * 1000) / 1000,
          keywords: Math.round(kwScore * 1000) / 1000,
          title: Math.round(titleScore * 1000) / 1000,
          partial: Math.round(partialScore * 1000) / 1000,
        },
      });
    }
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}

/** Invalida el cache de situaciones (llamar si se actualiza la DB). */
export function invalidateSearchCache(): void {
  cachedSituations = null;
}
