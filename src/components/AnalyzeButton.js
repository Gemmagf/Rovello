import React from 'react';
import { motion } from 'framer-motion';

const AnalyzeButton = ({ onAnalyze, isAnalyzing, disabled }) => {
  const actualDisabled = disabled || isAnalyzing;

  return (
    <motion.button
      onClick={onAnalyze}
      disabled={actualDisabled}
      className={`w-full px-8 py-4 rounded-btn font-semibold text-base flex items-center gap-3
        justify-center transition-colors duration-200 ${
        actualDisabled
          ? 'bg-sage-200 text-muted cursor-not-allowed'
          : 'bg-forest-900 text-cream-100 hover:bg-forest-700'
      }`}
      whileHover={!actualDisabled ? { scale: 1.01 } : {}}
      whileTap={!actualDisabled ? { scale: 0.98 } : {}}
    >
      {isAnalyzing ? (
        <>
          <motion.span
            style={{ fontSize: '1.25rem', display: 'inline-block' }}
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}
          >
            🍄
          </motion.span>
          <span>Analitzant...</span>
        </>
      ) : (
        <>
          <span style={{ fontSize: '1.25rem' }}>🍄</span>
          <span>Identificar bolet</span>
        </>
      )}
    </motion.button>
  );
};

export default AnalyzeButton;
