import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Colors } from '../../constants/colors';
import { Typography } from '../../constants/typography';
import { Card } from '../ui/Card';
import { openDialer, openWhatsApp } from '../../utils/phone';
import type { EmergencyContact } from '../../types/database';

interface Props {
  contact: EmergencyContact;
}

export function ContactCard({ contact }: Props) {
  return (
    <Card style={styles.card}>
      <Text style={styles.institution}>{contact.institution}</Text>
      <Text style={styles.description}>{contact.description}</Text>

      <View style={styles.meta}>
        {contact.is_free && <Text style={styles.freeLabel}>Gratuito</Text>}
        {contact.available_hours && (
          <Text style={styles.hours}>{contact.available_hours}</Text>
        )}
      </View>

      <View style={styles.buttons}>
        {contact.phone && (
          <Pressable
            onPress={() => openDialer(contact.phone!)}
            style={styles.callButton}
            accessibilityLabel={`Llamar a ${contact.institution}: ${contact.phone}`}
            accessibilityRole="button"
          >
            <Text style={styles.callButtonText}>Llamar {contact.phone}</Text>
          </Pressable>
        )}

        {contact.whatsapp && (
          <Pressable
            onPress={() => openWhatsApp(contact.whatsapp!)}
            style={styles.whatsappButton}
            accessibilityLabel={`WhatsApp a ${contact.institution}: ${contact.whatsapp}`}
            accessibilityRole="button"
          >
            <Text style={styles.whatsappButtonText}>WhatsApp</Text>
          </Pressable>
        )}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 0,
  },
  institution: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  meta: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  freeLabel: {
    ...Typography.caption,
    color: Colors.success,
    fontWeight: '600',
  },
  hours: {
    ...Typography.caption,
    color: Colors.textMuted,
  },
  buttons: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 12,
  },
  callButton: {
    flex: 1,
    backgroundColor: Colors.buttonCall,
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
  },
  callButtonText: {
    ...Typography.button,
    color: '#FFFFFF',
  },
  whatsappButton: {
    backgroundColor: Colors.buttonWhatsapp,
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
  },
  whatsappButtonText: {
    ...Typography.button,
    color: '#FFFFFF',
  },
});
