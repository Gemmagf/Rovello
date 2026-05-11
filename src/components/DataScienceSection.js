import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useT } from '../context/LanguageContext';

// ── Accordió reutilitzable ────────────────────────────────────────────────────
const Section = ({ title, emoji, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3.5
                   hover:bg-gray-50 transition-colors"
      >
        <span className="flex items-center gap-2 font-semibold text-gray-800 text-sm">
          <span>{emoji}</span>
          <span>{title}</span>
        </span>
        {open ? <ChevronUp size={15} className="text-gray-400" /> : <ChevronDown size={15} className="text-gray-400" />}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-1 border-t border-gray-50">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ── Component principal ───────────────────────────────────────────────────────
const DataScienceSection = () => {
  const { t } = useT();

  const metrics = [
    { value: '1.035',  label: t('dsSpecies'),    color: 'from-emerald-500 to-teal-600', icon: '🍄' },
    { value: '73.4%',  label: t('dsAccLabel'),   color: 'from-teal-500 to-cyan-600',    icon: '🎯' },
    { value: '50',     label: t('dsEpochsLabel'),color: 'from-blue-500 to-indigo-600',   icon: '🔄' },
    { value: '28M',    label: t('dsParamsLabel'),color: 'from-violet-500 to-purple-600', icon: '🧠' },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-4 text-white shadow-md"
      >
        <p className="text-emerald-100 text-xs font-medium uppercase tracking-wide mb-1">
          Rovello · {t('dsTitle')}
        </p>
        <p className="font-bold text-lg leading-tight">{t('dsTitle')}</p>
        <p className="text-emerald-100 text-sm mt-1">{t('dsSubtitle')}</p>
      </motion.div>

      {/* Mètriques clau */}
      <div className="grid grid-cols-2 gap-2">
        {metrics.map(({ value, label, color, icon }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.07 }}
            className={`bg-gradient-to-br ${color} rounded-2xl p-3 text-white shadow-sm`}
          >
            <div className="text-xl mb-0.5">{icon}</div>
            <div className="text-2xl font-black leading-none">{value}</div>
            <div className="text-xs opacity-80 mt-0.5 font-medium">{label}</div>
          </motion.div>
        ))}
      </div>

      {/* Arquitectura */}
      <Section emoji="🏗️" title={t('dsArchTitle')} defaultOpen={true}>
        <p className="text-xs text-gray-600 leading-relaxed mb-3">{t('dsArchDesc')}</p>
        {/* Flow diagram */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1">
          {t('dsArchFlow').map((step, i, arr) => (
            <React.Fragment key={step}>
              <div className="shrink-0 bg-emerald-50 border border-emerald-200 rounded-lg
                              px-2.5 py-1.5 text-center">
                <p className="text-xs font-semibold text-emerald-700 whitespace-nowrap">{step}</p>
              </div>
              {i < arr.length - 1 && (
                <span className="text-gray-300 font-bold shrink-0">→</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </Section>

      {/* Dades */}
      <Section emoji="📊" title={t('dsDataTitle')}>
        <dl className="space-y-2">
          {t('dsDataItems').map(([key, val]) => (
            <div key={key} className="flex items-start gap-2">
              <dt className="text-xs font-semibold text-gray-500 w-28 shrink-0">{key}</dt>
              <dd className="text-xs text-gray-700 leading-relaxed">{val}</dd>
            </div>
          ))}
        </dl>
      </Section>

      {/* Entrenament */}
      <Section emoji="⚙️" title={t('dsTrainTitle')}>
        <dl className="space-y-2 mb-4">
          {t('dsTrainItems').map(([key, val]) => (
            <div key={key} className="flex items-start gap-2">
              <dt className="text-xs font-semibold text-gray-500 w-24 shrink-0">{key}</dt>
              <dd className="text-xs text-gray-700 leading-relaxed">{val}</dd>
            </div>
          ))}
        </dl>

        {/* Fases d'entrenament amb barres d'accuràcia */}
        <div className="space-y-2.5">
          {t('dsTrainPhases').map(({ range, acc, label, best }) => (
            <div key={range}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono text-gray-500 w-16 shrink-0">{range}</span>
                <span className="text-xs text-gray-500 flex-1 pl-2 leading-tight">{label}</span>
                <span className={`text-xs font-bold ml-2 shrink-0 ${best ? 'text-emerald-600' : 'text-gray-500'}`}>
                  {acc}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full ${best ? 'bg-emerald-500' : 'bg-teal-300'}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${acc}%` }}
                    transition={{ delay: 0.2, duration: 0.8, ease: 'easeOut' }}
                  />
                </div>
                {best && (
                  <span className="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5
                                   rounded-full font-bold shrink-0">★</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Fusió bayesiana */}
      <Section emoji="🗺️" title={t('dsFusionTitle')}>
        <p className="text-xs text-gray-600 leading-relaxed mb-3">{t('dsFusionDesc')}</p>

        {/* Fórmula */}
        <div className="bg-gray-900 rounded-xl p-3 mb-3 overflow-x-auto">
          <code className="text-xs text-emerald-300 font-mono whitespace-nowrap">
            {t('dsFusionFormula')}
          </code>
        </div>

        <ul className="space-y-1.5">
          {t('dsFusionItems').map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
              <span className="shrink-0 text-teal-400 mt-0.5 font-bold">·</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </Section>

      {/* Limitacions */}
      <Section emoji="⚠️" title={t('dsLimTitle')}>
        <ul className="space-y-2.5">
          {t('dsLimitations').map(([icon, text], i) => (
            <li key={i} className="flex items-start gap-2.5">
              <span className="text-base shrink-0 mt-0.5">{icon}</span>
              <p className="text-xs text-gray-600 leading-relaxed">{text}</p>
            </li>
          ))}
        </ul>
      </Section>

      <p className="text-xs text-gray-400 text-center pb-2">
        Model: ConvNeXt-Tiny · PyTorch · iNaturalist · Apple M4 MPS
      </p>
    </div>
  );
};

export default DataScienceSection;
