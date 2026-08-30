import React from 'react';
import { motion } from 'framer-motion';
import { useT } from '../context/LanguageContext';

// Logo que replica les làmines radials de la imatge original
const RovelloLogo = ({ size = 48 }) => {
  const cx = 50, cy = 58, r = 34;
  const stemTop = cy;
  // 13 línies radials de 0° a 180° (semicercle superior)
  const angles = Array.from({ length: 13 }, (_, i) => (i * 180) / 12);
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="20" fill="#2E4B3A" />
      {/* Cap semicircle */}
      <path
        d={`M${cx - r} ${stemTop} A${r} ${r} 0 0 1 ${cx + r} ${stemTop} Z`}
        fill="#F2EFE6"
      />
      {/* Radial gill lines */}
      {angles.map((deg, i) => {
        const rad = (deg * Math.PI) / 180;
        const x2 = (cx + r * Math.cos(Math.PI - rad)).toFixed(2);
        const y2 = (stemTop - r * Math.sin(rad)).toFixed(2);
        return (
          <line key={i}
            x1={cx} y1={stemTop}
            x2={x2} y2={y2}
            stroke="#2E4B3A" strokeWidth="2.5" strokeLinecap="round"
          />
        );
      })}
      {/* Stem */}
      <rect x="43" y={stemTop} width="14" height="20" rx="5" fill="#F2EFE6" />
    </svg>
  );
};

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
      <div className="flex flex-col gap-3">
        {/* Row 1: logo+title on left, language pills on right */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-btn overflow-hidden shrink-0" style={{ width: 44, height: 44 }}>
              <RovelloLogo size={44} />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-tight">{t('appTitle')}</h1>
              <p className="text-cream-100/60 text-sm mt-0.5">{t('appSubtitle')}</p>
            </div>
          </div>
          <div className="flex gap-1 shrink-0">
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
        </div>

        {/* Row 2: disclaimer full width */}
        <p className="text-xs text-cream-100/50 leading-tight">
          {t('appDisclaimer')}
        </p>
      </div>
    </motion.div>
  );
};

export default Header;
