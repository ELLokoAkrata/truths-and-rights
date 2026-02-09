import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { Colors } from '../../constants/colors';
import { Typography } from '../../constants/typography';
import { Card } from '../ui/Card';
import type { SituationAction } from '../../types/database';

interface Props {
  action: SituationAction;
}

const ACTION_COLORS: Record<string, string> = {
  decir: Colors.actionDecir,
  hacer: Colors.actionHacer,
  no_hacer: Colors.actionNoHacer,
  grabar: Colors.actionGrabar,
  llamar: Colors.actionLlamar,
  documentar: Colors.actionDocumentar,
};

const ACTION_LABELS: Record<string, string> = {
  decir: 'DECIR',
  hacer: 'HACER',
  no_hacer: 'NO HACER',
  grabar: 'GRABAR',
  llamar: 'LLAMAR',
  documentar: 'DOCUMENTAR',
};

export function ActionStep({ action }: Props) {
  const color = ACTION_COLORS[action.action_type] || Colors.textMuted;
  const label = ACTION_LABELS[action.action_type] || action.action_type.toUpperCase();

  const handleCopyScript = async () => {
    if (action.script) {
      try {
        await Clipboard.setStringAsync(action.script);
      } catch {
        // Clipboard no disponible
      }
    }
  };

  return (
    <Card style={styles.card}>
      <View style={styles.header}>
        <View style={styles.stepCircle}>
          <Text style={styles.stepNumber}>{action.step_order}</Text>
        </View>
        <View style={[styles.typeBadge, { backgroundColor: color }]}>
          <Text style={styles.typeLabel}>{label}</Text>
        </View>
      </View>

      <Text style={styles.title}>{action.title}</Text>
      <Text style={styles.description}>{action.description}</Text>

      {action.script ? (
        <Pressable
          onPress={handleCopyScript}
          accessibilityLabel={`Texto sugerido: ${action.script}. Toca para copiar`}
          accessibilityRole="button"
          style={styles.scriptContainer}
        >
          <Text style={styles.scriptLabel}>Texto sugerido (toca para copiar):</Text>
          <Text style={styles.scriptText}>"{action.script}"</Text>
        </Pressable>
      ) : null}

      {action.warning ? (
        <View style={styles.warningContainer}>
          <Text style={styles.warningLabel}>Advertencia:</Text>
          <Text style={styles.warningText}>{action.warning}</Text>
        </View>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 8,
  },
  stepCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumber: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 16,
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  typeLabel: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  title: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  scriptContainer: {
    backgroundColor: Colors.surfaceElevated,
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    minHeight: 48,
  },
  scriptLabel: {
    ...Typography.caption,
    color: Colors.warning,
    marginBottom: 4,
  },
  scriptText: {
    ...Typography.body,
    color: Colors.textPrimary,
    fontStyle: 'italic',
  },
  warningContainer: {
    marginTop: 12,
    padding: 10,
    backgroundColor: 'rgba(231, 76, 60, 0.1)',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: Colors.error,
  },
  warningLabel: {
    ...Typography.caption,
    color: Colors.error,
    fontWeight: '700',
    marginBottom: 2,
  },
  warningText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
});
