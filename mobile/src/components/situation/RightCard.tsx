import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../../constants/colors';
import { Typography } from '../../constants/typography';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import type { SituationRight } from '../../types/database';

interface Props {
  right: SituationRight;
  isEmergencyActive: boolean;
}

export function RightCard({ right, isEmergencyActive }: Props) {
  const isSuspended = isEmergencyActive && !right.never_suspended && !right.applies;

  return (
    <Card style={[styles.card, isSuspended && styles.suspendedCard]}>
      <View style={styles.header}>
        {right.never_suspended && (
          <Badge label="NUNCA SE SUSPENDE" color={Colors.neverSuspended} />
        )}
        {isSuspended && (
          <Badge label="SUSPENDIDO EN EMERGENCIA" color={Colors.suspended} />
        )}
      </View>
      <Text style={[styles.title, isSuspended && styles.suspendedText]}>
        {right.title}
      </Text>
      <Text style={[styles.description, isSuspended && styles.suspendedText]}>
        {right.description}
      </Text>
      <Text style={styles.legalBasis}>{right.legal_basis}</Text>
      {right.notes ? (
        <Text style={styles.notes}>{right.notes}</Text>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 0,
  },
  suspendedCard: {
    opacity: 0.6,
    borderColor: Colors.suspended,
  },
  header: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 6,
  },
  title: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
    marginTop: 4,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  legalBasis: {
    ...Typography.caption,
    color: Colors.textMuted,
    marginTop: 8,
  },
  notes: {
    ...Typography.bodySmall,
    color: Colors.warning,
    marginTop: 6,
    fontStyle: 'italic',
  },
  suspendedText: {
    textDecorationLine: 'line-through',
  },
});
