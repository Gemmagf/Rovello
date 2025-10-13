import React from 'react';
import { motion } from 'framer-motion';

const AnalyzeButton = ({ onAnalyze, isAnalyzing, disabled }) => {
  const actualDisabled = disabled || !isAnalyzing;

  return (
    <motion.button
      onClick={onAnalyze}
      disabled={actualDisabled}
      className={`w-full md:w-auto px-8 py-4 rounded-2xl font-bold text-lg flex items-center gap-3 justify-center transition-all duration-300 relative overflow-hidden group ${
        actualDisabled
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : isAnalyzing
          ? 'bg-green-500 text-white shadow-lg hover:shadow-xl'
          : 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg hover:shadow-xl'
      }`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={!actualDisabled ? { scale: 1.05 } : {}}
      whileTap={!actualDisabled ? { scale: 0.95 } : {}}
      transition={{ duration: 0.3, type: 'spring' }}
    >
      <div className="flex items-center gap-3">
        {/* Bolet: gira només en "Identificar bolet" */}
        {isAnalyzing ? (
          <span style={{ fontSize: '1.5rem', display: 'inline-block' }}>🍄</span>
        ) : (
          <motion.span
            style={{ fontSize: '1.5rem', display: 'inline-block' }}
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          >
            🍄
          </motion.span>
        )}

        {/* Text del botó */}
        <span>{isAnalyzing ? 'Analitzant...' : 'Identificar bolet'}</span>
      </div>

      {/* Efecte d’ones només quan analitza */}
      {isAnalyzing && (
        <motion.div
          className="absolute inset-0 bg-white/20 rounded-2xl"
          initial={{ scale: 0, opacity: 1 }}
          animate={{
            scale: [1, 1.5, 2],
            opacity: [1, 0.5, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeOut',
          }}
        />
      )}
    </motion.button>
  );
};

export default AnalyzeButton;
