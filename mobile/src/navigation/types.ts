/**
 * Tipos de navegacion para toda la app.
 */

export type RootStackParamList = {
  MainTabs: undefined;
  Situation: { situationId: string; title: string };
  SearchResults: { query: string };
};

export type TabParamList = {
  Home: undefined;
  Rights: undefined;
  Emergency: undefined;
  More: undefined;
};

export type MoreStackParamList = {
  MoreMenu: undefined;
  Myths: undefined;
  Contacts: undefined;
  About: undefined;
};
