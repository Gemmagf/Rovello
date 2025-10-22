import React from 'react';
import { motion } from 'framer-motion';
import { X, Image as ImageIcon } from 'lucide-react';

const ImagePreview = ({ imageSrc, onRemove }) => {
  return (
    <motion.div
      className="bg-white/80 backdrop-blur-xl border border-gray-200/50 rounded-3xl p-6 shadow-xl mb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ImageIcon className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-gray-800">
            Vista prèvia del teu bolet
          </h3>
        </div>
        <motion.button
          onClick={onRemove}
          className="p-2 rounded-full bg-red-50 hover:bg-red-100 text-red-500 transition-colors"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <X className="w-5 h-5" />
        </motion.button>
      </div>
      <motion.img
        src={imageSrc}
        alt="Bolet pujat"
        className="w-full max-w-md mx-auto rounded-2xl shadow-md"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      />
    </motion.div>
  );
};

export default ImagePreview;
