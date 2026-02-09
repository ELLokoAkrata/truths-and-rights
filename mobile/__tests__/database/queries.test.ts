/**
 * Tests para las interfaces de queries.
 * Verifica que los tipos y la estructura de las queries son correctas.
 * Las queries SQL reales se prueban con la DB en emulador.
 */

import { getSeverityInfo } from '../../src/utils/severity';
import { Colors } from '../../src/constants/colors';
import { APP_VERSION, DB_VERSION, DB_FILENAME } from '../../src/constants/config';

describe('getSeverityInfo', () => {
  it('retorna info correcta para low', () => {
    const info = getSeverityInfo('low');
    expect(info.color).toBe(Colors.severityLow);
    expect(info.label).toBe('Bajo');
  });

  it('retorna info correcta para medium', () => {
    const info = getSeverityInfo('medium');
    expect(info.color).toBe(Colors.severityMedium);
    expect(info.label).toBe('Medio');
  });

  it('retorna info correcta para high', () => {
    const info = getSeverityInfo('high');
    expect(info.color).toBe(Colors.severityHigh);
    expect(info.label).toBe('Alto');
  });

  it('retorna info correcta para critical', () => {
    const info = getSeverityInfo('critical');
    expect(info.color).toBe(Colors.severityCritical);
    expect(info.label).toBe('Critico');
  });

  it('retorna medium como fallback para valores desconocidos', () => {
    const info = getSeverityInfo('unknown');
    expect(info.color).toBe(Colors.severityMedium);
    expect(info.label).toBe('Medio');
  });
});

describe('config', () => {
  it('tiene version de app 0.4.0', () => {
    expect(APP_VERSION).toBe('0.4.0');
  });

  it('tiene version de DB definida', () => {
    expect(DB_VERSION).toBeTruthy();
    // Formato ISO date
    expect(DB_VERSION).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('tiene nombre de DB correcto', () => {
    expect(DB_FILENAME).toBe('truths_and_rights_pe.db');
  });
});

describe('Colors', () => {
  it('tiene colores de fondo definidos', () => {
    expect(Colors.background).toBeTruthy();
    expect(Colors.surface).toBeTruthy();
  });

  it('tiene colores de severidad definidos', () => {
    expect(Colors.severityLow).toBeTruthy();
    expect(Colors.severityMedium).toBeTruthy();
    expect(Colors.severityHigh).toBeTruthy();
    expect(Colors.severityCritical).toBeTruthy();
  });

  it('tiene colores de emergencia definidos', () => {
    expect(Colors.emergencyBg).toBeTruthy();
    expect(Colors.emergencyBorder).toBeTruthy();
    expect(Colors.emergencyText).toBeTruthy();
  });

  it('tiene colores de acciones definidos', () => {
    expect(Colors.actionDecir).toBeTruthy();
    expect(Colors.actionHacer).toBeTruthy();
    expect(Colors.actionNoHacer).toBeTruthy();
  });
});
