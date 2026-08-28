import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

const ResultDisplay = ({ result, isLoading }) => {
  if (isLoading) {
    return (
      <motion.div
        className="bg-white border border-sage-200 rounded-card p-8 text-center flex flex-col items-center"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
          className="mb-4"
        >
          <Loader2 className="w-10 h-10 text-forest-700" strokeWidth={1.5} />
        </motion.div>
        <p className="text-ink font-medium mb-1">Analitzant el teu bolet...</p>
        <p className="text-muted text-sm">Un moment, si us plau.</p>
      </motion.div>
    );
  }

  if (!result) return null;

  const isEdible = result.edible;

  // Etiqueta de comestibilitat amb icona + color (accessible: mai sols pel color)
  const edibilityLabel = isEdible ? 'Comestible' : 'Tòxic / No recomanat';
  const edibilityIcon  = isEdible ? '✓' : '✕';
  const edibilityBg    = isEdible
    ? 'bg-green-50 text-green-800 border border-green-200'
    : 'bg-red-50 text-red-800 border border-red-200';

  return (
    <motion.div
      className="bg-white border border-sage-200 rounded-card p-6 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {/* Capçalera */}
      <div className="flex items-start gap-3 mb-4">
        <div className="mt-0.5 shrink-0">
          {isEdible
            ? <CheckCircle className="w-6 h-6 text-green-600" strokeWidth={1.5} />
            : <AlertCircle className="w-6 h-6 text-red-600"   strokeWidth={1.5} />
          }
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-ink leading-tight">{result.name}</h3>
          {result.scientificName && (
            <p className="text-sm text-muted italic mt-0.5">{result.scientificName}</p>
          )}
        </div>
        {result.confidence != null && (
          <span className="shrink-0 text-xs font-medium text-sage-500 bg-cream-100
                           px-2.5 py-1 rounded-pill border border-sage-200">
            {Math.round(result.confidence * 100)}%
          </span>
        )}
      </div>

      {/* Descripció */}
      {result.description && (
        <p className="text-muted text-sm mb-4 leading-relaxed">{result.description}</p>
      )}

      {/* Etiqueta comestibilitat */}
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-semibold mb-4 ${edibilityBg}`}>
        <span>{edibilityIcon}</span>
        <span>{edibilityLabel}</span>
      </span>

      {/* Consell */}
      {result.tips && (
        <div className="bg-cream-50 border border-sage-200 p-4 rounded-input">
          <h4 className="text-xs font-semibold text-ink uppercase tracking-wide mb-2">
            Consell de l'expert
          </h4>
          <p className="text-sm text-muted leading-relaxed">{result.tips}</p>
        </div>
      )}
    </motion.div>
  );
};

export default ResultDisplay;
