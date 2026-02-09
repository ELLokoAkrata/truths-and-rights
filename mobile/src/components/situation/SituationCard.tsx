import React from 'react';
import { Text, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../../constants/colors';
import { Typography } from '../../constants/typography';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { getSeverityInfo } from '../../utils/severity';
import type { Situation } from '../../types/database';

interface Props {
  situation: Situation;
  onPress: () => void;
}

export function SituationCard({ situation, onPress }: Props) {
  const severity = getSeverityInfo(situation.severity);

  return (
    <Pressable
      onPress={onPress}
      accessibilityLabel={`${situation.title}. Severidad ${severity.label}`}
      accessibilityRole="button"
      accessibilityHint="Toca para ver tus derechos en esta situacion"
      style={({ pressed }) => pressed && styles.pressed}
    >
      <Card style={styles.card}>
        <Badge label={severity.label} color={severity.color} />
        <Text style={styles.title} numberOfLines={2}>{situation.title}</Text>
        <Text style={styles.description} numberOfLines={2}>{situation.description}</Text>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 0,
  },
  pressed: {
    opacity: 0.8,
  },
  title: {
    ...Typography.h3,
    color: Colors.textPrimary,
    marginTop: 8,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
});
