import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { SearchBar } from '../components/ui/SearchBar';
import { SectionHeader } from '../components/ui/SectionHeader';
import { SituationCard } from '../components/situation/SituationCard';
import { EmergencyBanner } from '../components/EmergencyBanner';
import { useSituations } from '../hooks/useSituations';
import { useEmergencyContext } from '../hooks/useEmergencyContext';
import { useDataUpdate } from '../hooks/useDataUpdate';
import type { RootStackParamList } from '../navigation/types';
import type { Situation } from '../types/database';

type Nav = NativeStackNavigationProp<RootStackParamList>;

export function HomeScreen() {
  const navigation = useNavigation<Nav>();
  const { situations, loading } = useSituations();
  const { context, isActive } = useEmergencyContext();
  const { updateAvailable } = useDataUpdate();
  const [query, setQuery] = useState('');

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      navigation.navigate('SearchResults', { query: query.trim() });
    }
  }, [navigation, query]);

  const handleSituationPress = useCallback((situation: Situation) => {
    navigation.navigate('Situation', {
      situationId: situation.id,
      title: situation.title,
    });
  }, [navigation]);

  const renderHeader = () => (
    <View>
      <View style={styles.header}>
        <Text style={styles.title} accessibilityRole="header">
          Truths & Rights
        </Text>
        <Text style={styles.subtitle}>
          Tus derechos ante intervenciones policiales
        </Text>
      </View>

      <SearchBar
        value={query}
        onChangeText={setQuery}
        onSubmit={handleSearch}
        placeholder="Describe tu situacion..."
      />

      {updateAvailable && (
        <View style={styles.updateBanner}>
          <Text style={styles.updateText}>
            Hay una actualizacion de datos disponible
          </Text>
        </View>
      )}

      {isActive && context && (
        <EmergencyBanner
          context={context}
          onPress={() => navigation.getParent()?.navigate('Emergency')}
        />
      )}

      <SectionHeader title="SITUACIONES" subtitle="Selecciona la que se parece a la tuya" />
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
      <FlatList
        data={situations}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.cardWrapper}>
            <SituationCard
              situation={item}
              onPress={() => handleSituationPress(item)}
            />
          </View>
        )}
        ListHeaderComponent={renderHeader}
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
  header: {
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 8,
  },
  title: {
    ...Typography.h1,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  list: {
    paddingBottom: 24,
  },
  cardWrapper: {
    paddingHorizontal: 16,
  },
  loadingText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 100,
  },
  updateBanner: {
    backgroundColor: Colors.info,
    paddingVertical: 8,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 8,
  },
  updateText: {
    ...Typography.bodySmall,
    color: '#FFFFFF',
    textAlign: 'center',
  },
});
