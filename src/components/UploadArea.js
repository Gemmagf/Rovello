import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Image as ImageIcon, Camera, Plus, X } from 'lucide-react';
import { useT } from '../context/LanguageContext';
import PhotoCropper from './PhotoCropper';

export const MAX_PHOTOS = 3;

/**
 * Selecció de fotos. Es poden afegir fins a MAX_PHOTOS fotos del MATEIX bolet
 * (barret, làmines, peu…), cadascuna amb el seu enquadrament.
 *  - photosRef.current = [{ file, crop }]  (sempre actualitzat; el llegeix App en analitzar)
 *  - onCountChange(n) quan canvia el nombre de fotos
 */
const UploadArea = ({ photosRef, onCountChange }) => {
  const { t } = useT();
  const [dragActive, setDragActive] = useState(false);
  const [photos, setPhotos] = useState([]);       // { id, file, url }
  const [active, setActive] = useState(0);
  const crops = useRef(new Map());
  const nextId = useRef(1);

  const publish = (list) => {
    if (photosRef) photosRef.current = list.map((p) => ({ file: p.file, crop: crops.current.get(p.id) || null }));
  };

  useEffect(() => {
    publish(photos);
    if (onCountChange) onCountChange(photos.length);
  }, [photos]); // eslint-disable-line

  const addFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setPhotos((prev) => {
      if (prev.length >= MAX_PHOTOS) return prev;
      const next = [...prev, { id: nextId.current++, file, url: URL.createObjectURL(file) }];
      setActive(next.length - 1);
      return next;
    });
  };

  const removeAt = (i) => {
    setPhotos((prev) => {
      const gone = prev[i];
      if (gone) { URL.revokeObjectURL(gone.url); crops.current.delete(gone.id); }
      const next = prev.filter((_, j) => j !== i);
      setActive((a) => Math.max(0, Math.min(next.length - 1, a > i ? a - 1 : a)));
      return next;
    });
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    addFile(e.dataTransfer.files?.[0]);
  };
  const handleFileSelect = (e) => {
    addFile(e.target.files?.[0]);
    e.target.value = ''; // permet tornar a triar el mateix fitxer
  };

  return (
    <motion.div
      className={`relative bg-white border-2 rounded-card p-5 sm:p-6 text-center transition-colors duration-300 ${
        dragActive ? 'border-forest-700 bg-cream-50' : 'border-sage-200'
      }`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
    >
      {/* Inputs: galeria/arxius i càmera (mòbil) */}
      <input id="file-upload" type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
      <input id="camera-upload" type="file" accept="image/*" capture="environment"
        onChange={handleFileSelect} className="hidden" />

      {photos.length > 0 ? (
        <div className="flex flex-col items-center gap-3">
          {/* Un enquadrador per foto (només es mostra l'activa; les altres conserven l'enquadrament) */}
          {photos.map((p, i) => (
            <div key={p.id} className={i === active ? 'w-full' : 'hidden'}>
              <PhotoCropper src={p.url}
                onCropChange={(c) => { crops.current.set(p.id, c); publish(photos); }} />
            </div>
          ))}

          {/* Tira de miniatures + afegir */}
          <div className="flex items-center justify-center gap-2 flex-wrap">
            {photos.map((p, i) => (
              <div key={p.id} className="relative">
                <button type="button" onClick={() => setActive(i)}
                  className={`block w-14 h-14 rounded-input overflow-hidden border-2 transition-colors ${
                    i === active ? 'border-forest-900' : 'border-sage-200'}`}
                  aria-label={`${t('photoN')} ${i + 1}`}>
                  <img src={p.url} alt="" className="w-full h-full object-cover" draggable={false} />
                </button>
                <button type="button" onClick={() => removeAt(i)} aria-label={t('removePhoto')}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-pill bg-white border border-sage-200
                             text-muted hover:text-alert flex items-center justify-center shadow-sm">
                  <X size={12} strokeWidth={2.2} />
                </button>
              </div>
            ))}
            {photos.length < MAX_PHOTOS && (
              <label htmlFor="file-upload"
                className="w-14 h-14 rounded-input border-2 border-dashed border-sage-200 text-forest-700 cursor-pointer
                           flex flex-col items-center justify-center hover:bg-cream-100 transition-colors"
                aria-label={t('addPhoto')}>
                <Plus size={18} strokeWidth={1.8} />
              </label>
            )}
          </div>
          <p className="text-xs text-muted leading-relaxed max-w-[340px]">
            {photos.length < MAX_PHOTOS ? t('multiPhotoHint') : t('photoReady')}
          </p>
        </div>
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
