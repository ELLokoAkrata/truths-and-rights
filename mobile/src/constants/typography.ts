import { TextStyle } from 'react-native';

/**
 * Escalas tipograficas — legibles bajo estres, sin fuentes custom.
 * Usa la fuente del sistema (Roboto en Android).
 */
export const Typography: Record<string, TextStyle> = {
  // Titulos
  h1: {
    fontSize: 28,
    fontWeight: '700',
    lineHeight: 34,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 22,
    fontWeight: '700',
    lineHeight: 28,
  },
  h3: {
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 24,
  },

  // Cuerpo
  body: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
  },
  bodyBold: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
  },

  // UI
  caption: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  button: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24,
  },

  // Numeros grandes (limites de tiempo)
  bigNumber: {
    fontSize: 48,
    fontWeight: '700',
    lineHeight: 56,
  },
  bigNumberUnit: {
    fontSize: 18,
    fontWeight: '400',
    lineHeight: 24,
  },
} as const;
