import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useRoute } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { SectionHeader } from '../components/ui/SectionHeader';
import { Badge } from '../components/ui/Badge';
import { RightCard } from '../components/situation/RightCard';
import { ActionStep } from '../components/situation/ActionStep';
import { TimeLimitCard } from '../components/situation/TimeLimitCard';
import { ContactCard } from '../components/situation/ContactCard';
import { DisclaimerFooter } from '../components/DisclaimerFooter';
import { useSituationDetails } from '../hooks/useSituationDetails';
import { useEmergencyContext } from '../hooks/useEmergencyContext';
import { getSeverityInfo } from '../utils/severity';
import type { RootStackParamList } from '../navigation/types';

type Route = NativeStackScreenProps<RootStackParamList, 'Situation'>['route'];

export function SituationScreen() {
  const route = useRoute<Route>();
  const { situationId } = route.params;
  const { situation, details, loading } = useSituationDetails(situationId);
  const { isActive: isEmergencyActive } = useEmergencyContext();

  if (loading || !situation || !details) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  const severity = getSeverityInfo(situation.severity);

  // Filtrar derechos: en contexto normal y, si hay emergencia, mostrar el estado
  const normalRights = details.rights.filter(r => r.context_id === 'normal');
  const uniqueRights = normalRights.filter(
    (r, i, arr) => arr.findIndex(x => x.right_id === r.right_id) === i
  );

  // Ordenar: nunca suspendidos primero
  const sortedRights = [...uniqueRights].sort((a, b) => {
    if (a.never_suspended && !b.never_suspended) return -1;
    if (!a.never_suspended && b.never_suspended) return 1;
    return 0;
  });

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Badge label={severity.label} color={severity.color} />
        <Text style={styles.title}>{situation.title}</Text>
        <Text style={styles.description}>{situation.description}</Text>
      </View>

      {/* Derechos */}
      {sortedRights.length > 0 && (
        <View>
          <SectionHeader
            title="TUS DERECHOS"
            subtitle={isEmergencyActive ? 'Filtrados por estado de emergencia' : undefined}
          />
          {sortedRights.map((right) => (
            <View key={`${right.right_id}-${right.context_id}`} style={styles.cardWrapper}>
              <RightCard right={right} isEmergencyActive={isEmergencyActive} />
            </View>
          ))}
        </View>
      )}

      {/* Acciones */}
      {details.actions.length > 0 && (
        <View>
          <SectionHeader title="QUE HACER PASO A PASO" />
          {details.actions.map((action) => (
            <View key={`${action.action_id}-${action.step_order}`} style={styles.cardWrapper}>
              <ActionStep action={action} />
            </View>
          ))}
        </View>
      )}

      {/* Limites de tiempo */}
      {details.time_limits.length > 0 && (
        <View>
          <SectionHeader title="LIMITES DE TIEMPO" />
          {details.time_limits.map((tl) => (
            <View key={tl.id} style={styles.cardWrapper}>
              <TimeLimitCard timeLimit={tl} isEmergencyActive={isEmergencyActive} />
            </View>
          ))}
        </View>
      )}

      {/* Contactos */}
      {details.contacts.length > 0 && (
        <View>
          <SectionHeader title="A QUIEN LLAMAR" />
          {details.contacts.map((contact) => (
            <View key={contact.id} style={styles.cardWrapper}>
              <ContactCard contact={contact} />
            </View>
          ))}
        </View>
      )}

      <DisclaimerFooter />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    paddingBottom: 40,
  },
  header: {
    padding: 16,
    paddingTop: 20,
  },
  title: {
    ...Typography.h1,
    color: Colors.textPrimary,
    marginTop: 12,
  },
  description: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginTop: 8,
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
