import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import type { Context } from '../types/database';

interface Props {
  context: Context;
  onPress?: () => void;
}

export function EmergencyBanner({ context, onPress }: Props) {
  const regions = context.active_regions
    ? JSON.parse(context.active_regions).join(', ')
    : '';

  return (
    <Pressable
      onPress={onPress}
      style={styles.container}
      accessibilityLabel={`Estado de emergencia activo: ${context.name}`}
      accessibilityRole="button"
      accessibilityHint="Toca para ver detalles del estado de emergencia"
    >
      <View style={styles.header}>
        <Text style={styles.icon}>▲</Text>
        <Text style={styles.title}>ESTADO DE EMERGENCIA ACTIVO</Text>
      </View>
      <Text style={styles.decree}>{context.decree_number}</Text>
      {regions ? <Text style={styles.regions}>{regions}</Text> : null}
      {context.end_date ? (
        <Text style={styles.date}>Vigente hasta: {context.end_date}</Text>
      ) : null}
      <Text style={styles.cta}>Toca para ver que derechos se afectan</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.emergencyBg,
    borderWidth: 1,
    borderColor: Colors.emergencyBorder,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  icon: {
    color: Colors.emergencyText,
    fontSize: 16,
    marginRight: 8,
  },
  title: {
    ...Typography.label,
    color: Colors.emergencyText,
    fontSize: 13,
  },
  decree: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
    marginTop: 4,
  },
  regions: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  date: {
    ...Typography.bodySmall,
    color: Colors.warning,
    marginTop: 4,
  },
  cta: {
    ...Typography.caption,
    color: Colors.textMuted,
    marginTop: 8,
  },
});
