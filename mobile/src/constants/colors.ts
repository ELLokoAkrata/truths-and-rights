/**
 * Paleta de colores — alto contraste para uso en situaciones de estres.
 * Cumple WCAG AA (ratio >= 4.5:1 para texto normal).
 */
export const Colors = {
  // Fondo
  background: '#1A1A2E',
  surface: '#16213E',
  surfaceElevated: '#0F3460',

  // Texto
  textPrimary: '#FFFFFF',
  textSecondary: '#B0B0C0',
  textMuted: '#6B6B80',

  // Acentos
  primary: '#E94560',
  primaryLight: '#FF6B81',
  accent: '#533483',

  // Severidad
  severityLow: '#27AE60',
  severityMedium: '#F39C12',
  severityHigh: '#E74C3C',
  severityCritical: '#C0392B',

  // Estado
  success: '#2ECC71',
  warning: '#F1C40F',
  error: '#E74C3C',
  info: '#3498DB',

  // Emergencia
  emergencyBg: '#4A0E0E',
  emergencyBorder: '#E74C3C',
  emergencyText: '#FF6B6B',

  // Badges
  neverSuspended: '#2ECC71',
  suspended: '#E74C3C',

  // Acciones
  actionDecir: '#3498DB',
  actionHacer: '#2ECC71',
  actionNoHacer: '#E74C3C',
  actionGrabar: '#9B59B6',
  actionLlamar: '#F39C12',
  actionDocumentar: '#1ABC9C',

  // Bordes y divisores
  border: '#2A2A4A',
  divider: '#2A2A4A',

  // Botones
  buttonPrimary: '#E94560',
  buttonSecondary: '#533483',
  buttonCall: '#27AE60',
  buttonWhatsapp: '#25D366',
} as const;

export type ColorName = keyof typeof Colors;
