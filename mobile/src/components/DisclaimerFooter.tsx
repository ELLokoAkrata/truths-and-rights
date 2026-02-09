import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';

export function DisclaimerFooter() {
  return (
    <View style={styles.container} accessibilityLabel="Aviso legal">
      <Text style={styles.text}>
        Esta informacion NO es asesoria legal. Para casos especificos, consulta con un abogado.
      </Text>
      <Text style={styles.text}>
        Los datos provienen de fuentes oficiales pero pueden no estar actualizados.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    marginTop: 16,
    marginHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  text: {
    ...Typography.caption,
    color: Colors.textMuted,
    textAlign: 'center',
    marginBottom: 4,
  },
});
