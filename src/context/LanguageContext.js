import React, { createContext, useContext, useState } from 'react';
import { translations } from '../i18n/translations';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState(
    () => localStorage.getItem('rovello_lang') || 'ca'
  );

  const changeLang = (l) => {
    setLang(l);
    localStorage.setItem('rovello_lang', l);
  };

  /**
   * t(key) → retorna el valor de la clau (string, array o qualsevol tipus).
   * Fallback a 'ca' si la clau no existeix en l'idioma actual.
   */
  const t = (key) => {
    const val = translations[lang]?.[key];
    if (val !== undefined) return val;
    return translations.ca?.[key] ?? key;
  };

  return (
    <LanguageContext.Provider value={{ lang, changeLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useT = () => useContext(LanguageContext);
