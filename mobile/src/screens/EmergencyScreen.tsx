import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useEmergencyContext } from '../hooks/useEmergencyContext';

export function EmergencyScreen() {
  const { context, isActive, loading } = useEmergencyContext();

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  const suspendedRights = context?.affects_rights
    ? JSON.parse(context.affects_rights) as string[]
    : [];

  const regions = context?.active_regions
    ? JSON.parse(context.active_regions) as string[]
    : [];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.headerArea}>
        <Text style={styles.screenTitle} accessibilityRole="header">
          Estado de Emergencia
        </Text>
      </View>

      {!isActive || !context ? (
        <Card>
          <View style={styles.noEmergency}>
            <Text style={styles.noEmergencyTitle}>Sin estado de emergencia activo</Text>
            <Text style={styles.noEmergencyText}>
              Actualmente no hay un estado de emergencia vigente que afecte tus derechos.
              Todos tus derechos constitucionales estan plenamente vigentes.
            </Text>
          </View>
        </Card>
      ) : (
        <View>
          {/* Status */}
          <Card style={styles.emergencyCard}>
            <Badge label="ACTIVO" color={Colors.emergencyBorder} />
            <Text style={styles.contextName}>{context.name}</Text>
            <Text style={styles.contextDesc}>{context.description}</Text>

            {context.decree_number && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Decreto:</Text>
                <Text style={styles.infoValue}>{context.decree_number}</Text>
              </View>
            )}

            {context.start_date && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Inicio:</Text>
                <Text style={styles.infoValue}>{context.start_date}</Text>
              </View>
            )}

            {context.end_date && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Vence:</Text>
                <Text style={[styles.infoValue, styles.dateWarning]}>{context.end_date}</Text>
              </View>
            )}
          </Card>

          {/* Regiones */}
          {regions.length > 0 && (
            <Card>
              <Text style={styles.sectionLabel}>REGIONES AFECTADAS</Text>
              {regions.map((region) => (
                <Text key={region} style={styles.regionItem}>
                  {region}
                </Text>
              ))}
            </Card>
          )}

          {/* Derechos suspendidos */}
          {suspendedRights.length > 0 && (
            <Card>
              <Text style={styles.sectionLabel}>DERECHOS SUSPENDIDOS</Text>
              {suspendedRights.map((right) => (
                <View key={right} style={styles.suspendedItem}>
                  <Badge label="SUSPENDIDO" color={Colors.suspended} />
                  <Text style={styles.suspendedText}>
                    {right.replace(/_/g, ' ')}
                  </Text>
                </View>
              ))}
            </Card>
          )}

          {/* Derechos que nunca se suspenden */}
          <Card>
            <Text style={[styles.sectionLabel, { color: Colors.neverSuspended }]}>
              DERECHOS QUE NUNCA SE SUSPENDEN
            </Text>
            <Text style={styles.neverSuspendedText}>
              Incluso en estado de emergencia, SIEMPRE conservas:
            </Text>
            {[
              'Dignidad humana',
              'Debido proceso',
              'Comunicaciones privadas (celular)',
              'Habeas corpus',
              'Derecho a un abogado',
              'Prohibicion de tortura y tratos degradantes',
            ].map((right) => (
              <View key={right} style={styles.neverItem}>
                <Badge label="NUNCA SE SUSPENDE" color={Colors.neverSuspended} />
                <Text style={styles.neverItemText}>{right}</Text>
              </View>
            ))}
          </Card>
        </View>
      )}
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
  headerArea: {
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 8,
  },
  screenTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
  },
  emergencyCard: {
    borderColor: Colors.emergencyBorder,
    borderWidth: 1,
  },
  contextName: {
    ...Typography.h2,
    color: Colors.textPrimary,
    marginTop: 12,
  },
  contextDesc: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginTop: 8,
  },
  infoRow: {
    flexDirection: 'row',
    marginTop: 8,
    gap: 8,
  },
  infoLabel: {
    ...Typography.bodySmall,
    color: Colors.textMuted,
    fontWeight: '600',
  },
  infoValue: {
    ...Typography.bodySmall,
    color: Colors.textPrimary,
  },
  dateWarning: {
    color: Colors.warning,
    fontWeight: '600',
  },
  sectionLabel: {
    ...Typography.label,
    color: Colors.textSecondary,
    marginBottom: 12,
  },
  regionItem: {
    ...Typography.body,
    color: Colors.textPrimary,
    paddingVertical: 4,
  },
  suspendedItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 6,
  },
  suspendedText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textTransform: 'capitalize',
    flex: 1,
  },
  neverSuspendedText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginBottom: 12,
  },
  neverItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 6,
  },
  neverItemText: {
    ...Typography.body,
    color: Colors.textPrimary,
    flex: 1,
  },
  noEmergency: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  noEmergencyTitle: {
    ...Typography.h3,
    color: Colors.success,
    marginBottom: 8,
  },
  noEmergencyText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  loadingText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 100,
  },
});
