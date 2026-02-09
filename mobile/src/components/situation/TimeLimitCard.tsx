import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../../constants/colors';
import { Typography } from '../../constants/typography';
import { Card } from '../ui/Card';
import type { TimeLimit } from '../../types/database';

interface Props {
  timeLimit: TimeLimit;
  isEmergencyActive: boolean;
}

export function TimeLimitCard({ timeLimit, isEmergencyActive }: Props) {
  const hours = isEmergencyActive && timeLimit.max_hours_emergency != null
    ? timeLimit.max_hours_emergency
    : timeLimit.max_hours;

  const hoursLabel = hours === Math.floor(hours) ? String(Math.floor(hours)) : String(hours);

  return (
    <Card style={styles.card}>
      <Text style={styles.description}>{timeLimit.description}</Text>
      <View style={styles.hoursRow}>
        <Text style={styles.hoursNumber}>{hoursLabel}</Text>
        <Text style={styles.hoursUnit}>horas{'\n'}maximo</Text>
      </View>

      {isEmergencyActive && timeLimit.max_hours_emergency != null &&
        timeLimit.max_hours_emergency !== timeLimit.max_hours && (
        <Text style={styles.emergencyNote}>
          Plazo modificado por estado de emergencia (normal: {timeLimit.max_hours}h)
        </Text>
      )}

      {timeLimit.applies_to !== 'todos' && (
        <Text style={styles.appliesTo}>
          Aplica a: {timeLimit.applies_to === 'nacional' ? 'Nacionales' : 'Extranjeros'}
        </Text>
      )}

      <View style={styles.expiryRow}>
        <Text style={styles.expiryLabel}>Si se excede:</Text>
        <Text style={styles.expiryAction}>{timeLimit.after_expiry_action}</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 0,
  },
  description: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
  },
  hoursRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 8,
    marginTop: 12,
    marginBottom: 8,
  },
  hoursNumber: {
    ...Typography.bigNumber,
    color: Colors.error,
  },
  hoursUnit: {
    ...Typography.bigNumberUnit,
    color: Colors.textSecondary,
  },
  emergencyNote: {
    ...Typography.caption,
    color: Colors.warning,
    fontStyle: 'italic',
    marginBottom: 8,
  },
  appliesTo: {
    ...Typography.caption,
    color: Colors.textMuted,
    marginBottom: 8,
  },
  expiryRow: {
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  expiryLabel: {
    ...Typography.caption,
    color: Colors.error,
    fontWeight: '700',
    marginBottom: 2,
  },
  expiryAction: {
    ...Typography.bodySmall,
    color: Colors.textPrimary,
  },
});
