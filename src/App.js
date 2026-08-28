import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LanguageProvider, useT } from './context/LanguageContext';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import AnalyzeButton from './components/AnalyzeButton';
import ResultDisplay from './components/ResultDisplay';
import NearbyMushrooms from './components/NearbyMushrooms';
import PilzkontrolleInfo from './components/PilzkontrolleInfo';
import DataScienceSection from './components/DataScienceSection';
import { analyzeMushroom, requestGeolocation } from './utils/mushroomAnalyzer';

const API_URL = process.env.REACT_APP_API_URL || 'https://rovello-backend.onrender.com';
fetch(`${API_URL}/health`).catch(() => {});

const TAB_IDENTIFICA    = 'identifica';
const TAB_DESCOBREIX    = 'descobreix';
const TAB_PILZKONTROLLE = 'pilzkontrolle';
const TAB_DATA          = 'data';

const AppInner = () => {
  const { t } = useT();
  const [activeTab, setActiveTab] = useState(TAB_IDENTIFICA);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [geo, setGeo] = useState(null);
  const [geoStatus, setGeoStatus] = useState('idle');

  const month = new Date().getMonth() + 1;

  const tryGeolocation = () => {
    setGeoStatus('requesting');
    requestGeolocation().then((loc) => {
      if (loc) { setGeo(loc); setGeoStatus('granted'); }
      else      { setGeoStatus('denied'); }
    });
  };

  useEffect(() => { tryGeolocation(); }, []); // eslint-disable-line

  const handleImageSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setResult(null);
    try {
      const context = { month, ...(geo || {}) };
      const analysis = await analyzeMushroom(selectedFile, context);
      setResult(analysis);
    } catch {
      setResult({
        name: 'Error en la detecció',
        description: 'Alguna cosa ha anat malament. Prova amb una altra foto més clara.',
        edible: false, toxicity: 'Revisa la imatge',
        tips: "Assegura't que la foto sigui nítida i ben il·luminada.",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const TABS = [
    { key: TAB_IDENTIFICA,    icon: '🔍', label: t('tabIdentifica') },
    { key: TAB_DESCOBREIX,    icon: '🗺️', label: t('tabDescobreix') },
    { key: TAB_PILZKONTROLLE, icon: '🔬', label: t('tabPilzkontrolle') },
    { key: TAB_DATA,          icon: '📊', label: t('tabData') },
  ];

  return (
    <div className="min-h-screen bg-cream-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <Header />

          {/* Geo status */}
          <div className="mt-3 text-center text-xs text-muted">
            {geoStatus === 'granted' && geo && (
              <span className={geo.byIP ? 'text-amber-600' : 'text-forest-700'}>
                📍 {geo.lat.toFixed(3)}°, {geo.lon.toFixed(3)}°
                {' · '}{geo.byIP ? '🌐 ubicació per IP (aprox.)' : t('geoActive')}
              </span>
            )}
            {geoStatus === 'denied' && (
              <span className="text-amber-600">
                📍 {t('geoDenied')}{' '}
                <button onClick={tryGeolocation}
                  className="underline hover:text-amber-800 font-medium ml-1">
                  {t('geoRetry')}
                </button>
              </span>
            )}
            {geoStatus === 'requesting' && (
              <span>⏳ {t('geoRequesting')}</span>
            )}
          </div>

          {/* Tab bar */}
          <div className="flex bg-white rounded-card p-1 mt-5 shadow-sm border border-sage-200">
            {TABS.map(({ key, icon, label }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex-1 flex items-center justify-center gap-1 py-2.5 rounded-btn
                  text-xs font-semibold transition-all duration-200
                  ${activeTab === key
                    ? 'bg-forest-900 text-cream-100 shadow-sm'
                    : 'text-muted hover:text-ink'
                  }`}
              >
                <span>{icon}</span>
                <span className="hidden sm:inline">{label}</span>
                <span className="sm:hidden">{label.substring(0, 4)}</span>
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="mt-6">
            <AnimatePresence mode="wait">
              {activeTab === TAB_IDENTIFICA && (
                <motion.div key="identifica"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}
                  className="space-y-6"
                >
                  <UploadArea onImageSelect={handleImageSelect} />
                  {selectedFile && (
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                      exit={{ y: -20, opacity: 0 }}>
                      <AnalyzeButton onAnalyze={handleAnalyze}
                        isAnalyzing={isAnalyzing} disabled={!selectedFile} />
                    </motion.div>
                  )}
                  <AnimatePresence mode="wait">
                    <ResultDisplay key={result ? 'result' : 'loading'}
                      result={result} isLoading={isAnalyzing} />
                  </AnimatePresence>
                  {result && result.contextUsed && (
                    <p className="text-xs text-center text-forest-700">{t('contextUsed')}</p>
                  )}
                </motion.div>
              )}

              {activeTab === TAB_DESCOBREIX && (
                <motion.div key="descobreix"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
                  <NearbyMushrooms geo={geo} month={month} />
                </motion.div>
              )}

              {activeTab === TAB_PILZKONTROLLE && (
                <motion.div key="pilzkontrolle"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
                  <PilzkontrolleInfo />
                </motion.div>
              )}

              {activeTab === TAB_DATA && (
                <motion.div key="data"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
                  <DataScienceSection />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        <motion.div className="mt-12 text-center text-muted text-xs"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}>
          🍄 {t('footerMain')}
          <br />
          <span className="text-sage-500">{t('footerSub')}</span>
        </motion.div>
      </div>
    </div>
  );
};

const App = () => (
  <LanguageProvider>
    <AppInner />
  </LanguageProvider>
);

export default App;
