import React from 'react';
import { motion } from 'framer-motion';

const MushroomIcon = () => (
  <svg
    className="w-8 h-8"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Cap del bolet */}
    <ellipse cx="12" cy="8" rx="6" ry="4" fill="currentColor" />
    {/* Tija */}
    <rect x="10" y="12" width="4" height="8" rx="1" fill="currentColor" />
    {/* Puntets blancs per diversió */}
    <circle cx="11" cy="6" r="0.5" fill="white" />
    <circle cx="13" cy="7" r="0.5" fill="white" />
    <circle cx="14" cy="5" r="0.5" fill="white" />
  </svg>
);

const Header = () => {
  return (
    <motion.div
      className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-8 rounded-b-3xl shadow-xl"
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="container mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <motion.div
            className="p-4 bg-white/20 rounded-2xl backdrop-blur-sm"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <MushroomIcon />
          </motion.div>
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">MushroomScan</h1>
            <p className="text-green-100 font-medium">
              Detecta si el teu bolet és amic o enemic — o potser només un impostor!
            </p>
          </div>
        </div>
        <motion.div
          className="text-sm opacity-90"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          ⚠️ Això no és cap consell mèdic — informa’t bé abans de tastar res!
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Header;
