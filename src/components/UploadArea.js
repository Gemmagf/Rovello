import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Image } from 'lucide-react';

const UploadArea = ({ onImageSelect }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file?.type.startsWith('image/')) processFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file?.type.startsWith('image/')) processFile(file);
  };

  const processFile = (file) => {
    const reader = new FileReader();
    reader.onload = (ev) => {
      setSelectedImage(ev.target.result);
      onImageSelect(file);
    };
    reader.readAsDataURL(file);
  };

  return (
    <motion.div
      className={`relative bg-white border-2 rounded-card p-8 text-center transition-all duration-300 ${
        dragActive
          ? 'border-forest-700 bg-cream-50 shadow-md'
          : 'border-sage-200 hover:border-forest-700/40'
      }`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {selectedImage ? (
        <motion.div className="flex flex-col items-center gap-4"
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
          <img
            src={selectedImage}
            alt="Bolet seleccionat"
            className="w-64 h-64 object-cover rounded-card shadow-sm border border-sage-200"
          />
          <p className="text-muted text-sm font-medium">
            Foto preparada! Prem el botó per identificar.
          </p>
          <label htmlFor="file-upload"
            className="text-xs text-forest-700 underline cursor-pointer hover:text-forest-900">
            Canviar foto
          </label>
          <input id="file-upload" type="file" accept="image/*"
            onChange={handleFileSelect} className="hidden" />
        </motion.div>
      ) : (
        <>
          <div className="mx-auto w-16 h-16 bg-cream-100 border border-sage-200 rounded-btn
                          flex items-center justify-center mb-5">
            <Upload className="w-7 h-7 text-forest-700" strokeWidth={1.5} />
          </div>
          <h2 className="text-lg font-semibold text-ink mb-1">Puja el teu bolet</h2>
          <p className="text-muted text-sm mb-6">
            Arrossega la imatge aquí o fes clic per seleccionar-la
          </p>
          <label htmlFor="file-upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-forest-900 text-cream-100
                       rounded-btn font-medium text-sm cursor-pointer
                       hover:bg-forest-700 transition-colors">
            <Image className="w-4 h-4" strokeWidth={1.5} />
            Selecciona foto
          </label>
          <input id="file-upload" type="file" accept="image/*"
            onChange={handleFileSelect} className="hidden" />
          <p className="mt-4 text-xs text-sage-500">O arrossega aquí</p>
        </>
      )}
    </motion.div>
  );
};

export default UploadArea;
