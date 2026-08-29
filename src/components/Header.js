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
          <div className="rounded-btn overflow-hidden" style={{ width: 48, height: 48 }}>
            <svg width="48" height="48" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <rect width="100" height="100" rx="22" fill="#2E4B3A" />
              {/* Cap outline */}
              <path d="M50 68 L50 32 A30 30 0 0 1 80 62 Z" fill="#F2EFE6" />
              <path d="M50 68 L50 32 A30 30 0 0 0 20 62 Z" fill="#F2EFE6" />
              {/* Radial gill lines on right half */}
              {[15,30,45,60,75].map((deg, i) => {
                const rad = (deg * Math.PI) / 180;
                return (
                  <line key={`r${i}`}
                    x1="50" y1="68"
                    x2={(50 + 32 * Math.sin(rad)).toFixed(1)}
                    y2={(68 - 32 * Math.cos(rad)).toFixed(1)}
                    stroke="#2E4B3A" strokeWidth="2.2" strokeLinecap="round"
                  />
                );
              })}
              {/* Radial gill lines on left half */}
              {[15,30,45,60,75].map((deg, i) => {
                const rad = (deg * Math.PI) / 180;
                return (
                  <line key={`l${i}`}
                    x1="50" y1="68"
                    x2={(50 - 32 * Math.sin(rad)).toFixed(1)}
                    y2={(68 - 32 * Math.cos(rad)).toFixed(1)}
                    stroke="#2E4B3A" strokeWidth="2.2" strokeLinecap="round"
                  />
                );
              })}
              {/* Tija */}
              <rect x="43" y="68" width="14" height="18" rx="4" fill="#F2EFE6" />
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
