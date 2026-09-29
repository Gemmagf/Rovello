import React from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2 } from 'lucide-react';
import { useT } from '../context/LanguageContext';

const AnalyzeButton = ({ onAnalyze, isAnalyzing, disabled }) => {
  const { t } = useT();
  const actualDisabled = disabled || isAnalyzing;

  return (
    <motion.button
      onClick={onAnalyze}
      disabled={actualDisabled}
      className={`w-full min-h-[52px] px-6 py-3.5 rounded-btn font-semibold text-base flex items-center gap-2.5
        justify-center transition-colors duration-200 ${
        actualDisabled
          ? 'bg-sage-200 text-muted cursor-not-allowed'
          : 'bg-forest-900 text-cream-100 hover:bg-forest-700'
      }`}
      whileHover={!actualDisabled ? { scale: 1.01 } : {}}
      whileTap={!actualDisabled ? { scale: 0.98 } : {}}
    >
      {isAnalyzing
        ? <Loader2 className="w-5 h-5 animate-spin" strokeWidth={2} />
        : <Search className="w-5 h-5" strokeWidth={2} />}
      <span>{isAnalyzing ? t('analyzing') : t('analyzeBtn')}</span>
    </motion.button>
  );
};

export default AnalyzeButton;
