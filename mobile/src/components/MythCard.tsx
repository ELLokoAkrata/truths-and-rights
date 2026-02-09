import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { Card } from './ui/Card';
import type { Myth } from '../types/database';

interface Props {
  myth: Myth;
}

export function MythCard({ myth }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Pressable
      onPress={() => setExpanded(!expanded)}
      accessibilityLabel={`Mito: ${myth.myth}. Realidad: ${myth.reality}`}
      accessibilityRole="button"
      accessibilityHint={expanded ? 'Toca para colapsar' : 'Toca para ver la explicacion'}
    >
      <Card>
        <Text style={styles.label}>MITO</Text>
        <Text style={styles.myth}>{myth.myth}</Text>
        <Text style={styles.realityLabel}>REALIDAD</Text>
        <Text style={styles.reality}>{myth.reality}</Text>
        {expanded && (
          <View style={styles.explanation}>
            <Text style={styles.explanationText}>{myth.explanation}</Text>
          </View>
        )}
        <Text style={styles.toggle}>
          {expanded ? 'Toca para colapsar' : 'Toca para ver mas'}
        </Text>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  label: {
    ...Typography.caption,
    color: Colors.error,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 4,
  },
  myth: {
    ...Typography.body,
    color: Colors.textSecondary,
    fontStyle: 'italic',
    marginBottom: 12,
  },
  realityLabel: {
    ...Typography.caption,
    color: Colors.success,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 4,
  },
  reality: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
  },
  explanation: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  explanationText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  toggle: {
    ...Typography.caption,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: 12,
  },
});
