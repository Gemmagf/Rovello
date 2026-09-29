import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Image as ImageIcon, Camera } from 'lucide-react';
import { useT } from '../context/LanguageContext';

const UploadArea = ({ onImageSelect }) => {
  const { t } = useT();
  const [dragActive, setDragActive] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const processFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setSelectedImage(ev.target.result);
      onImageSelect(file);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    processFile(e.dataTransfer.files?.[0]);
  };

  const handleFileSelect = (e) => {
    processFile(e.target.files?.[0]);
    e.target.value = ''; // permet tornar a triar el mateix fitxer
  };

  return (
    <motion.div
      className={`relative bg-white border-2 rounded-card p-5 sm:p-6 text-center transition-colors duration-300 ${
        dragActive ? 'border-forest-700 bg-cream-50' : 'border-sage-200'
      }`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Inputs: galeria/arxius i càmera (mòbil) */}
      <input id="file-upload" type="file" accept="image/*"
        onChange={handleFileSelect} className="hidden" />
      <input id="camera-upload" type="file" accept="image/*" capture="environment"
        onChange={handleFileSelect} className="hidden" />

      {selectedImage ? (
        <motion.div className="flex flex-col items-center gap-3"
          initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}>
          <img
            src={selectedImage}
            alt=""
            className="w-full max-w-[280px] aspect-square object-cover rounded-card border border-sage-200"
          />
          <p className="text-muted text-sm">{t('photoReady')}</p>
          <label htmlFor="file-upload"
            className="text-sm font-medium text-forest-700 underline underline-offset-2 cursor-pointer hover:text-forest-900">
            {t('changePhoto')}
          </label>
        </motion.div>
      ) : (
        <>
          <div className="mx-auto w-14 h-14 bg-cream-100 border border-sage-200 rounded-btn
                          flex items-center justify-center mb-4">
            <Upload className="w-6 h-6 text-forest-700" strokeWidth={1.5} />
          </div>
          <h2 className="text-lg font-semibold text-ink mb-1">{t('uploadTitle')}</h2>
          <p className="text-muted text-sm mb-5 max-w-xs mx-auto leading-relaxed">{t('uploadHint')}</p>
          <div className="flex flex-col sm:flex-row gap-2.5 justify-center">
            <label htmlFor="file-upload"
              className="inline-flex items-center justify-center gap-2 min-h-[48px] px-6 py-3 bg-forest-900 text-cream-100
                         rounded-btn font-medium text-sm cursor-pointer hover:bg-forest-700 transition-colors">
              <ImageIcon className="w-4 h-4" strokeWidth={1.5} />
              {t('choosePhoto')}
            </label>
            <label htmlFor="camera-upload"
              className="sm:hidden inline-flex items-center justify-center gap-2 min-h-[48px] px-6 py-3 bg-cream-100 text-forest-900
                         border border-sage-200 rounded-btn font-medium text-sm cursor-pointer hover:bg-sage-200/60 transition-colors">
              <Camera className="w-4 h-4" strokeWidth={1.5} />
              {t('takePhoto')}
            </label>
          </div>
          <p className="mt-4 text-xs text-sage-500 hidden sm:block">{t('dragHere')}</p>
        </>
      )}
    </motion.div>
  );
};

export default UploadArea;
