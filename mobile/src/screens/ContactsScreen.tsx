import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { ContactCard } from '../components/situation/ContactCard';
import { useContacts } from '../hooks/useContacts';
import type { EmergencyContact } from '../types/database';

export function ContactsScreen() {
  const { contacts, loading } = useContacts();

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
        data={contacts}
        keyExtractor={(item: EmergencyContact) => item.id}
        renderItem={({ item }: { item: EmergencyContact }) => (
          <View style={styles.cardWrapper}>
            <ContactCard contact={item} />
          </View>
        )}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          <View style={styles.headerArea}>
            <Text style={styles.intro}>
              Numeros de ayuda gratuita para emergencias y denuncias. Todos funcionan 24/7 salvo indicacion contraria.
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
  cardWrapper: {
    paddingHorizontal: 16,
  },
  loadingText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 100,
  },
});
