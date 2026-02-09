import React, { useState, useMemo } from 'react';
import { View, Text, FlatList, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { useRights } from '../hooks/useRights';
import type { Right } from '../types/database';

const CATEGORIES: Record<string, string> = {
  all: 'Todos',
  libertad: 'Libertad',
  integridad: 'Integridad',
  comunicaciones: 'Comunicaciones',
  propiedad: 'Propiedad',
  debido_proceso: 'Debido Proceso',
  dignidad: 'Dignidad',
};

export function RightsListScreen() {
  const { rights, loading } = useRights();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = useMemo(() => {
    const cats = new Set(rights.map(r => r.category));
    return ['all', ...Array.from(cats)];
  }, [rights]);

  const filteredRights = useMemo(() => {
    if (selectedCategory === 'all') return rights;
    return rights.filter(r => r.category === selectedCategory);
  }, [rights, selectedCategory]);

  const renderRight = ({ item }: { item: Right }) => (
    <View style={styles.cardWrapper}>
      <Card>
        <View style={styles.badges}>
          {item.never_suspended && (
            <Badge label="NUNCA SE SUSPENDE" color={Colors.neverSuspended} />
          )}
          <Badge
            label={CATEGORIES[item.category] || item.category}
            color={Colors.accent}
          />
        </View>
        <Text style={styles.rightTitle}>{item.title}</Text>
        <Text style={styles.rightDesc}>{item.description}</Text>
        <Text style={styles.legalBasis}>{item.legal_basis}</Text>
      </Card>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerArea}>
        <Text style={styles.screenTitle} accessibilityRole="header">Derechos</Text>
      </View>

      {/* Filtros */}
      <View style={styles.filterRow}>
        <FlatList
          horizontal
          data={categories}
          keyExtractor={(item) => item}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterContent}
          renderItem={({ item }) => (
            <Pressable
              onPress={() => setSelectedCategory(item)}
              style={[
                styles.filterChip,
                selectedCategory === item && styles.filterChipActive,
              ]}
              accessibilityLabel={`Filtrar por ${CATEGORIES[item] || item}`}
              accessibilityRole="button"
              accessibilityState={{ selected: selectedCategory === item }}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedCategory === item && styles.filterTextActive,
                ]}
              >
                {CATEGORIES[item] || item}
              </Text>
            </Pressable>
          )}
        />
      </View>

      <SectionHeader
        title={`${filteredRights.length} DERECHOS`}
      />

      <FlatList
        data={filteredRights}
        keyExtractor={(item) => item.id}
        renderItem={renderRight}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
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
    paddingTop: 60,
    paddingBottom: 8,
  },
  screenTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
  },
  filterRow: {
    marginVertical: 8,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    minHeight: 48,
    justifyContent: 'center',
  },
  filterChipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  filterText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  filterTextActive: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  list: {
    paddingBottom: 24,
  },
  cardWrapper: {
    paddingHorizontal: 0,
  },
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 6,
  },
  rightTitle: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
    marginTop: 4,
  },
  rightDesc: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  legalBasis: {
    ...Typography.caption,
    color: Colors.textMuted,
    marginTop: 8,
  },
  loadingText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 100,
  },
});
