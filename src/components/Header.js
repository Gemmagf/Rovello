import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { useT } from '../context/LanguageContext';

// Logo que replica les làmines radials de la imatge original
export const RovelloLogo = ({ size = 48 }) => {
  // Cèrcol fi + 25 làmines radials crema sobre verd + tija trapezoïdal
  const cx = 50, cy = 59, rRim = 36, rGill = 32.5;
  const gills = Array.from({ length: 25 }, (_, i) => (i * 7.5 * Math.PI) / 180);
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ maxWidth: size, maxHeight: size }} xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="20" fill="#2E4B3A" />
      <path d={`M${cx - rRim} ${cy} A${rRim} ${rRim} 0 0 1 ${cx + rRim} ${cy}`}
        fill="none" stroke="#F2EFE6" strokeWidth="2.4" strokeLinecap="round" />
      {gills.map((a, i) => (
        <line key={i} x1={cx} y1={cy}
          x2={(cx + rGill * Math.cos(Math.PI - a)).toFixed(2)} y2={(cy - rGill * Math.sin(a)).toFixed(2)}
          stroke="#F2EFE6" strokeWidth="1.9" strokeLinecap="round" />
      ))}
      <path d={`M${cx - 5.5} 55 L${cx + 5.5} 55 L${cx + 8} 86 L${cx - 8} 86 Z`}
        fill="#F2EFE6" stroke="#F2EFE6" strokeWidth="4" strokeLinejoin="round" />
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
      className="bg-forest-900 text-cream-100 px-5 py-5 sm:px-6 sm:py-6 rounded-card shadow-lg"
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="flex flex-col gap-3">
        {/* Row 1: logo+title on left, language pills on right */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
            <div className="rounded-btn overflow-hidden shrink-0 w-10 h-10 sm:w-11 sm:h-11">
              <RovelloLogo size={44} />
            </div>
            <h1 className="text-lg sm:text-2xl font-bold tracking-tight leading-none truncate">{t('appTitle')}</h1>
          </div>
          <div className="flex gap-1 shrink-0">
            {LANGS.map(({ code, label }) => (
              <button
                key={code}
                onClick={() => changeLang(code)}
                className={`text-[11px] sm:text-xs font-semibold px-2 sm:px-2.5 py-1 rounded-pill transition-all
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

        {/* Eslògan a tota amplada */}
        <p className="text-cream-100/75 text-sm leading-snug">{t('appSubtitle')}</p>

        {/* Row 2: disclaimer full width */}
        <p className="flex items-start gap-1.5 text-xs text-cream-100/60 leading-snug">
          <AlertTriangle size={13} className="shrink-0 mt-px" />
          <span>{t('appDisclaimer')}</span>
        </p>
      </div>
    </motion.div>
  );
};

export default Header;
