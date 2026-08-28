import React from 'react';
import { motion } from 'framer-motion';
import { useT } from '../context/LanguageContext';

const LANGS = [
  { code: 'ca', label: 'CA' },
  { code: 'en', label: 'EN' },
  { code: 'de', label: 'DE' },
];

const Header = () => {
  const { t, lang, changeLang } = useT();

  return (
    <motion.div
      className="bg-forest-900 text-cream-100 px-6 py-6 rounded-card shadow-lg"
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Logo + títol */}
        <div className="flex items-center gap-4">
          <div className="p-3 bg-cream-100/10 rounded-btn">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
              {/* Làmines radials inspirades en el logo */}
              {Array.from({ length: 12 }).map((_, i) => {
                const angle = (i / 12) * Math.PI;
                const x1 = 12 + 5 * Math.cos(angle - Math.PI / 2);
                const y1 = 8  + 4 * Math.sin(angle - Math.PI / 2);
                return (
                  <line key={i}
                    x1="12" y1="13"
                    x2={x1.toFixed(2)} y2={y1.toFixed(2)}
                    stroke="#F2EFE6" strokeWidth="1.2" strokeLinecap="round"
                  />
                );
              })}
              {/* Tija */}
              <rect x="10.5" y="13" width="3" height="6" rx="1.5" fill="#F2EFE6" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{t('appTitle')}</h1>
            <p className="text-cream-100/60 text-sm mt-0.5">{t('appSubtitle')}</p>
          </div>
        </div>

        {/* Language + disclaimer */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          <div className="flex gap-1">
            {LANGS.map(({ code, label }) => (
              <button
                key={code}
                onClick={() => changeLang(code)}
                className={`text-xs font-semibold px-2.5 py-1 rounded-pill transition-all
                  ${lang === code
                    ? 'bg-cream-100 text-forest-900'
                    : 'bg-cream-100/10 text-cream-100/70 hover:bg-cream-100/20'
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
          <p className="text-xs text-cream-100/50 text-right max-w-[180px] leading-tight">
            {t('appDisclaimer')}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default Header;
