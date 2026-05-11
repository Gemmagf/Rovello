import React from 'react';
import { motion } from 'framer-motion';
import { useT } from '../context/LanguageContext';

const MushroomIcon = () => (
  <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="8" rx="6" ry="4" fill="currentColor" />
    <rect x="10" y="12" width="4" height="8" rx="1" fill="currentColor" />
    <circle cx="11" cy="6" r="0.5" fill="white" />
    <circle cx="13" cy="7" r="0.5" fill="white" />
    <circle cx="14" cy="5" r="0.5" fill="white" />
  </svg>
);

const LANGS = [
  { code: 'ca', label: 'CA' },
  { code: 'en', label: 'EN' },
  { code: 'de', label: 'DE' },
];

const Header = () => {
  const { t, lang, changeLang } = useT();

  return (
    <motion.div
      className="bg-gradient-to-r from-green-500 to-emerald-600 text-white
                 px-6 py-6 rounded-b-3xl shadow-xl"
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Logo + títol */}
        <div className="flex items-center gap-4">
          <motion.div
            className="p-4 bg-white/20 rounded-2xl backdrop-blur-sm"
            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          >
            <MushroomIcon />
          </motion.div>
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">{t('appTitle')}</h1>
            <p className="text-green-100 font-medium text-sm mt-0.5">{t('appSubtitle')}</p>
          </div>
        </div>

        {/* Selector d'idioma + disclaimer */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          {/* Language switcher */}
          <div className="flex gap-1">
            {LANGS.map(({ code, label }) => (
              <button
                key={code}
                onClick={() => changeLang(code)}
                className={`text-xs font-bold px-2.5 py-1 rounded-lg transition-all
                  ${lang === code
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'bg-white/20 text-white/80 hover:bg-white/30'
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
          {/* Disclaimer */}
          <motion.p
            className="text-xs text-green-100/80 text-right max-w-[180px] leading-tight"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('appDisclaimer')}
          </motion.p>
        </div>
      </div>
    </motion.div>
  );
};

export default Header;
