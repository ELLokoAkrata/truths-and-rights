import React from 'react';
import { View, Text, ScrollView, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { Card } from '../components/ui/Card';
import { APP_VERSION, DB_VERSION } from '../constants/config';
import { openURL } from '../utils/phone';

export function AboutScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Card>
        <Text style={styles.appName}>Truths & Rights</Text>
        <Text style={styles.version}>Version {APP_VERSION}</Text>
        <Text style={styles.dbVersion}>Datos: {DB_VERSION}</Text>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Que es esta app</Text>
        <Text style={styles.text}>
          Truths & Rights es una app ciudadana que informa tus derechos ante intervenciones policiales en Peru.
          Toda la informacion proviene de fuentes legales oficiales y verificables.
        </Text>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Aviso legal</Text>
        <Text style={styles.text}>
          Esta aplicacion NO es asesoria legal. La informacion presentada tiene fines educativos y de orientacion.
          Para casos especificos, consulta con un abogado.
        </Text>
        <Text style={[styles.text, { marginTop: 8 }]}>
          Los datos provienen de la Constitucion Politica del Peru, el Codigo Procesal Penal,
          jurisprudencia del Tribunal Constitucional y tratados internacionales de derechos humanos.
        </Text>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Fuentes</Text>
        <Text style={styles.text}>
          43 fuentes legales verificadas, incluyendo:
        </Text>
        <Text style={styles.sourceItem}>Constitucion Politica del Peru (1993)</Text>
        <Text style={styles.sourceItem}>Codigo Procesal Penal (DL 957)</Text>
        <Text style={styles.sourceItem}>Codigo Penal (DL 635)</Text>
        <Text style={styles.sourceItem}>Sentencias del Tribunal Constitucional</Text>
        <Text style={styles.sourceItem}>Convencion Americana sobre Derechos Humanos</Text>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Codigo abierto</Text>
        <Text style={styles.text}>
          Este proyecto es software libre (GPL v3). El codigo fuente y todos los datos
          estan disponibles publicamente.
        </Text>
        <Pressable
          onPress={() => openURL('https://github.com/ELLokoAkrata/truths-and-rights')}
          style={styles.linkButton}
          accessibilityLabel="Ver codigo en GitHub"
          accessibilityRole="link"
        >
          <Text style={styles.linkText}>Ver en GitHub</Text>
        </Pressable>
        <Pressable
          onPress={() => openURL('https://ellokoakrata.github.io/truths-and-rights/')}
          style={styles.linkButton}
          accessibilityLabel="Ver portal web"
          accessibilityRole="link"
        >
          <Text style={styles.linkText}>Portal web</Text>
        </Pressable>
      </Card>

      <Card>
        <Text style={styles.sectionTitle}>Principio fundamental</Text>
        <Text style={[styles.text, styles.principle]}>
          Si no tiene fuente oficial verificable, no entra a la base de datos.
        </Text>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    paddingBottom: 40,
  },
  appName: {
    ...Typography.h1,
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  version: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 4,
  },
  dbVersion: {
    ...Typography.caption,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: 2,
  },
  sectionTitle: {
    ...Typography.h3,
    color: Colors.textPrimary,
    marginBottom: 8,
  },
  text: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  sourceItem: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    paddingLeft: 12,
    paddingVertical: 2,
  },
  linkButton: {
    marginTop: 10,
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: Colors.surfaceElevated,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 48,
    justifyContent: 'center',
  },
  linkText: {
    ...Typography.button,
    color: Colors.primary,
  },
  principle: {
    fontStyle: 'italic',
    color: Colors.warning,
  },
});
