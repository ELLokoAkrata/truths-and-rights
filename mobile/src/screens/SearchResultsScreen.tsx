import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp, NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { SearchBar } from '../components/ui/SearchBar';
import { SituationCard } from '../components/situation/SituationCard';
import { useDatabase } from '../hooks/useDatabase';
import { searchSituation } from '../database/search';
import type { RootStackParamList } from '../navigation/types';
import type { SearchResult } from '../types/database';

type Nav = NativeStackNavigationProp<RootStackParamList>;
type Route = NativeStackScreenProps<RootStackParamList, 'SearchResults'>['route'];

export function SearchResultsScreen() {
  const navigation = useNavigation<Nav>();
  const route = useRoute<Route>();
  const db = useDatabase();
  const [query, setQuery] = useState(route.params.query);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }
    const r = await searchSituation(db, q.trim(), 9);
    setResults(r);
    setSearched(true);
  }, [db]);

  // Buscar al montar con el query inicial
  useEffect(() => {
    doSearch(route.params.query);
  }, [route.params.query, doSearch]);

  // Buscar en tiempo real con debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      doSearch(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, doSearch]);

  return (
    <View style={styles.container}>
      <SearchBar
        value={query}
        onChangeText={setQuery}
        onSubmit={() => doSearch(query)}
        autoFocus
      />

      {searched && results.length === 0 && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyTitle}>No se encontraron resultados</Text>
          <Text style={styles.emptyText}>
            Intenta con otras palabras, por ejemplo:
          </Text>
          <Text style={styles.exampleText}>- "me piden el DNI"</Text>
          <Text style={styles.exampleText}>- "quieren revisar mi mochila"</Text>
          <Text style={styles.exampleText}>- "me llevan a la comisaria"</Text>
        </View>
      )}

      <FlatList
        data={results}
        keyExtractor={(item) => item.situation_id}
        renderItem={({ item }) => (
          <View style={styles.cardWrapper}>
            <SituationCard
              situation={{
                id: item.situation_id,
                title: item.title,
                description: item.description,
                severity: item.severity as 'low' | 'medium' | 'high' | 'critical',
                category: item.category,
                keywords: '',
                natural_queries: '',
                icon: null,
                parent_situation_id: null,
                display_order: 0,
                is_active: true,
              }}
              onPress={() =>
                navigation.navigate('Situation', {
                  situationId: item.situation_id,
                  title: item.title,
                })
              }
            />
            <Text style={styles.score}>
              Relevancia: {Math.round(item.score * 100)}%
            </Text>
          </View>
        )}
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
  list: {
    paddingBottom: 24,
  },
  cardWrapper: {
    paddingHorizontal: 16,
  },
  score: {
    ...Typography.caption,
    color: Colors.textMuted,
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  emptyState: {
    padding: 32,
    alignItems: 'center',
  },
  emptyTitle: {
    ...Typography.h3,
    color: Colors.textSecondary,
    marginBottom: 12,
  },
  emptyText: {
    ...Typography.bodySmall,
    color: Colors.textMuted,
    marginBottom: 8,
  },
  exampleText: {
    ...Typography.bodySmall,
    color: Colors.textMuted,
  },
});
