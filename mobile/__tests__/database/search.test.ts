/**
 * Tests para el motor de busqueda — verifica el port de search.py.
 * Usa funciones puras sin DB (testing de la logica de scoring).
 */

import { normalize, tokenize, tokensSinStopwords, STOPWORDS } from '../../src/utils/normalize';

describe('normalize', () => {
  it('convierte a minusculas', () => {
    expect(normalize('HOLA MUNDO')).toBe('hola mundo');
  });

  it('quita tildes', () => {
    expect(normalize('policía identificación')).toBe('policia identificacion');
  });

  it('quita puntuacion', () => {
    expect(normalize('¿me piden DNI?')).toBe('me piden dni');
  });

  it('colapsa espacios', () => {
    expect(normalize('  hola   mundo  ')).toBe('hola mundo');
  });

  it('maneja string vacio', () => {
    expect(normalize('')).toBe('');
    expect(normalize('   ')).toBe('');
  });

  it('maneja texto con dieresis', () => {
    expect(normalize('über')).toBe('uber');
  });
});

describe('tokenize', () => {
  it('divide texto en tokens unicos', () => {
    const tokens = tokenize('me piden DNI me piden documentos');
    expect(tokens).toEqual(new Set(['me', 'piden', 'dni', 'documentos']));
  });

  it('normaliza antes de tokenizar', () => {
    const tokens = tokenize('Policía IDENTIFICACIÓN');
    expect(tokens).toEqual(new Set(['policia', 'identificacion']));
  });
});

describe('tokensSinStopwords', () => {
  it('filtra stopwords comunes', () => {
    const tokens = tokensSinStopwords('me quieren revisar el celular');
    expect(tokens.has('me')).toBe(false);
    expect(tokens.has('el')).toBe(false);
    expect(tokens.has('quieren')).toBe(true);
    expect(tokens.has('revisar')).toBe(true);
    expect(tokens.has('celular')).toBe(true);
  });

  it('maneja texto de solo stopwords', () => {
    const tokens = tokensSinStopwords('me la el de');
    expect(tokens.size).toBe(0);
  });

  it('preserva palabras significativas', () => {
    const tokens = tokensSinStopwords('policia DNI documento mochila');
    expect(tokens.size).toBe(4);
  });
});

describe('STOPWORDS', () => {
  it('contiene stopwords comunes en espanol', () => {
    expect(STOPWORDS.has('me')).toBe(true);
    expect(STOPWORDS.has('de')).toBe(true);
    expect(STOPWORDS.has('el')).toBe(true);
    expect(STOPWORDS.has('la')).toBe(true);
  });

  it('no contiene palabras significativas', () => {
    expect(STOPWORDS.has('policia')).toBe(false);
    expect(STOPWORDS.has('derecho')).toBe(false);
    expect(STOPWORDS.has('celular')).toBe(false);
  });

  it('tiene al menos 50 stopwords', () => {
    expect(STOPWORDS.size).toBeGreaterThanOrEqual(50);
  });
});
