import { Linking } from 'react-native';

/**
 * Utilidades para abrir tel: y whatsapp://.
 */

/** Limpia un numero de telefono para uso en URL (quita espacios, guiones). */
function cleanPhone(phone: string): string {
  return phone.replace(/[\s\-()]/g, '');
}

/** Abre el dialer con el numero dado. */
export function openDialer(phone: string): void {
  const cleaned = cleanPhone(phone);
  Linking.openURL(`tel:${cleaned}`);
}

/** Abre WhatsApp con el numero dado (formato internacional, sin +). */
export function openWhatsApp(whatsapp: string, message?: string): void {
  let cleaned = cleanPhone(whatsapp);
  // Quitar el + inicial si existe
  if (cleaned.startsWith('+')) {
    cleaned = cleaned.substring(1);
  }
  let url = `whatsapp://send?phone=${cleaned}`;
  if (message) {
    url += `&text=${encodeURIComponent(message)}`;
  }
  Linking.openURL(url);
}

/** Abre una URL en el navegador. */
export function openURL(url: string): void {
  Linking.openURL(url);
}
