import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { MythCard } from '../components/MythCard';
import { useMyths } from '../hooks/useMyths';
import type { Myth } from '../types/database';

export function MythsScreen() {
  const { myths, loading } = useMyths();

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={myths}
        keyExtractor={(item: Myth) => item.id}
        renderItem={({ item }: { item: Myth }) => <MythCard myth={item} />}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          <View style={styles.headerArea}>
            <Text style={styles.intro}>
              Creencias comunes sobre derechos ciudadanos que no son ciertas. Toca cada una para ver la explicacion completa.
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  headerArea: {
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  intro: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  list: {
    paddingBottom: 24,
  },
  loadingText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 100,
  },
});
