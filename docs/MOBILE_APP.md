# App movil — Guia de desarrollo

## Tecnologias utilizadas

### React Native
Framework para crear apps moviles nativas usando JavaScript/TypeScript. Una sola base de codigo genera apps para Android e iOS. No es una app web empaquetada — genera componentes nativos reales.

### Expo
Plataforma que simplifica React Native. Sin Expo, necesitarias instalar Android Studio, Xcode, configurar SDKs y firmas manualmente. Expo maneja todo eso.

Usamos **Expo SDK 52** (ultima version estable).

### Expo Go
App gratuita que se instala en el telefono (Play Store / App Store). Funciona como "reproductor" de apps Expo durante el desarrollo. El servidor corre en tu PC, Expo Go en tu telefono descarga el codigo via WiFi y lo ejecuta.

**Solo se usa para desarrollo.** La app final es un APK/IPA independiente que no necesita Expo Go.

### SQLite (expo-sqlite)
Base de datos embebida dentro de la app. La DB se genera desde los JSON del proyecto (~256KB) y se incluye en el paquete de la app. Esto permite que funcione **offline** — toda la informacion legal esta en el telefono.

### Zustand
Libreria minima para estado global. Guarda preferencias del usuario (fecha de ultima actualizacion, si acepto disclaimer). Persiste en AsyncStorage.

### React Navigation
Sistema de navegacion entre pantallas. Maneja la barra inferior (tabs), las pantallas modales (situacion, busqueda), y la pila de navegacion (atras/adelante).

---

## Estructura de la app

```
mobile/
├── App.tsx                         # Punto de entrada
├── package.json                    # Dependencias
├── app.json                        # Configuracion de Expo
├── eas.json                        # Configuracion de builds (EAS)
├── tsconfig.json                   # TypeScript strict mode
├── babel.config.js                 # Configuracion de Babel
├── assets/
│   ├── db/truths_and_rights_pe.db  # Base de datos SQLite (copiada del build)
│   ├── icon.png                    # Icono de la app
│   ├── adaptive-icon.png           # Icono adaptativo (Android)
│   └── splash.png                  # Pantalla de carga
├── scripts/
│   └── copy-db.js                  # Copia DB de build/ a assets/db/
├── src/
│   ├── database/
│   │   ├── DatabaseProvider.tsx     # Context provider que inicializa la DB
│   │   ├── initDatabase.ts         # Copia la DB de assets al filesystem del telefono
│   │   ├── queries.ts              # Todas las consultas SQL
│   │   └── search.ts               # Motor de busqueda offline con scoring
│   ├── navigation/
│   │   ├── RootNavigator.tsx       # Navegacion raiz (tabs + modales)
│   │   ├── TabNavigator.tsx        # Barra inferior (Inicio, Derechos, Emergencia, Mas)
│   │   ├── MoreNavigator.tsx       # Sub-navegacion del tab "Mas"
│   │   └── types.ts                # Tipos de TypeScript para navegacion
│   ├── screens/                    # Una pantalla por archivo
│   │   ├── HomeScreen.tsx          # Buscador + situaciones frecuentes
│   │   ├── SituationScreen.tsx     # Detalle de situacion (derechos, acciones, contactos)
│   │   ├── RightsListScreen.tsx    # Todos los derechos con filtro por categoria
│   │   ├── EmergencyScreen.tsx     # Estado de emergencia actual
│   │   ├── SearchResultsScreen.tsx # Resultados de busqueda
│   │   ├── MythsScreen.tsx         # Mitos desmentidos
│   │   ├── ContactsScreen.tsx      # Telefonos de emergencia
│   │   ├── AboutScreen.tsx         # Acerca de
│   │   └── MoreMenuScreen.tsx      # Menu adicional
│   ├── components/
│   │   ├── EmergencyBanner.tsx     # Banner rojo de estado de emergencia
│   │   ├── DisclaimerFooter.tsx    # Disclaimer legal
│   │   ├── MythCard.tsx            # Tarjeta de mito
│   │   ├── situation/              # Componentes de la pantalla de situacion
│   │   │   ├── SituationCard.tsx
│   │   │   ├── RightCard.tsx
│   │   │   ├── ActionStep.tsx
│   │   │   ├── ContactCard.tsx
│   │   │   └── TimeLimitCard.tsx
│   │   └── ui/                     # Componentes reutilizables
│   │       ├── Badge.tsx
│   │       ├── Card.tsx
│   │       ├── SearchBar.tsx
│   │       └── SectionHeader.tsx
│   ├── hooks/                      # Custom hooks (cargan datos de la DB)
│   │   ├── useDatabase.ts
│   │   ├── useSituations.ts
│   │   ├── useSituationDetails.ts
│   │   ├── useEmergencyContext.ts
│   │   ├── useRights.ts
│   │   ├── useMyths.ts
│   │   ├── useContacts.ts
│   │   └── useDataUpdate.ts
│   ├── store/
│   │   └── useAppStore.ts          # Estado global (Zustand)
│   ├── constants/
│   │   ├── colors.ts               # Paleta de colores
│   │   ├── typography.ts           # Tipografia
│   │   └── config.ts               # Configuracion (DB filename, URLs, etc.)
│   ├── types/
│   │   └── database.ts             # Interfaces TypeScript para todas las tablas
│   └── utils/
│       ├── normalize.ts            # Normalizacion de texto espanol (acentos, etc.)
│       ├── phone.ts                # Abrir telefono, WhatsApp, URLs
│       └── severity.ts             # Mapeo de severidad a colores
└── __tests__/
    └── database/
        ├── queries.test.ts         # Tests de utilidades
        └── search.test.ts          # Tests del motor de busqueda
```

---

## Como funciona la DB en la app

1. `build_db.py` lee los JSON de `data/PE/` y genera `build/truths_and_rights_pe.db`
2. `scripts/copy-db.js` copia esa DB a `mobile/assets/db/`
3. Expo empaqueta `assets/db/` dentro de la app
4. Al abrir la app, `initDatabase.ts` copia la DB de assets al filesystem del telefono
5. `queries.ts` ejecuta consultas SQL contra esa DB local
6. Todo funciona offline — no se necesita internet

---

## Desarrollo: como probar la app

### Requisitos en tu PC

- Node.js 18+ instalado
- Python 3.9+ (para generar la DB)
- Tu telefono y PC en la misma red WiFi

### Requisitos en tu telefono

- Instalar **Expo Go** desde Play Store (Android) o App Store (iOS)

### Pasos

```bash
# 1. Instalar dependencias (solo la primera vez)
make mobile-install

# 2. Generar DB y copiarla a la app
make mobile-copy-db

# 3. Iniciar servidor de desarrollo
make mobile-start
```

Esto muestra un QR en la terminal. Escanea con Expo Go y la app se carga en tu telefono.

**Hot reload:** Cada vez que guardas un archivo, la app se actualiza automaticamente en tu telefono.

### Si algo falla

- **"Network error"**: Verifica que PC y telefono estan en la misma WiFi
- **"Unable to resolve module"**: Ejecuta `make mobile-install` de nuevo
- **DB no carga**: Ejecuta `make mobile-copy-db` y reinicia Expo

---

## Build de produccion (APK)

Para generar un APK que puedas instalar sin Expo Go:

```bash
make mobile-build-apk
```

Esto usa **EAS Build** (servicio de Expo). Necesitas cuenta en expo.dev (gratis). El APK se genera en la nube y lo descargas.

Para build local (sin EAS, necesita Android SDK):
```bash
cd mobile
npx expo run:android
```

---

## Pantallas de la app

| Pantalla | Que muestra | Como se llega |
|---|---|---|
| **Home** | Buscador + situaciones frecuentes + banner emergencia | Tab "Inicio" |
| **Situacion** | Derechos, acciones paso a paso, limites, contactos | Tocar una situacion |
| **Busqueda** | Resultados con score de relevancia | Escribir en buscador |
| **Derechos** | Todos los derechos, filtrable por categoria | Tab "Derechos" |
| **Emergencia** | Estado de emergencia: que se suspende y que NO | Tab "Emergencia" |
| **Mitos** | Mitos desmentidos con base legal | Tab "Mas" > Mitos |
| **Contactos** | Telefonos con boton de llamar directo | Tab "Mas" > Contactos |
| **Acerca de** | Version, fuentes, disclaimer | Tab "Mas" > Acerca de |

---

## Busqueda offline

El motor de busqueda (`search.ts`) usa un sistema de scoring:

| Factor | Peso | Ejemplo |
|---|---|---|
| Natural queries | 45% | "me piden DNI" coincide exacto con query del usuario |
| Keywords | 30% | "dni", "identidad", "documento" |
| Title | 15% | "La policia me pide DNI" |
| Parcial | 10% | Coincidencia parcial de tokens |

Normaliza texto espanol (acentos, mayusculas), elimina stopwords ("el", "la", "de"), y cachea resultados.

---

## Actualizacion de datos

La DB se embebe en la app al momento del build. Para actualizar datos:

1. Editar los JSON en `data/PE/`
2. `make build-pe` → regenera la DB
3. `make mobile-copy-db` → copia al proyecto
4. Nuevo build de la app

La app tambien puede verificar si hay datos nuevos consultando `status.json` del portal (cuando tiene internet), pero no descarga datos automaticamente — solo notifica.

---

## Tests

```bash
make mobile-test
```

Tests actuales:
- Normalizacion de texto espanol (acentos, puntuacion, espacios)
- Tokenizacion y stopwords
- Utilidades (severidad, colores, configuracion)

Pendiente: tests de integracion con la DB real en emulador.

---

## Pendiente (futuras versiones)

- [ ] Probar en dispositivos reales (Android + iOS)
- [ ] Boton de panico (grabar audio/video + compartir ubicacion)
- [ ] Notificaciones push cuando cambie un decreto
- [ ] Tests de integracion con DB
- [ ] Pantalla de error si la DB falla al cargar
- [ ] Modo offline indicator
- [ ] Accesibilidad (screen reader, contraste)
- [ ] Publicar en Play Store / App Store
