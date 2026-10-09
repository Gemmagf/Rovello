import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LanguageProvider, useT } from './context/LanguageContext';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import AnalyzeButton from './components/AnalyzeButton';
import ResultDisplay from './components/ResultDisplay';
import NearbyMushrooms from './components/NearbyMushrooms';
import PilzkontrolleInfo from './components/PilzkontrolleInfo';
import DataScienceSection from './components/DataScienceSection';
import LocalRules from './components/LocalRules';
import { Search, MapPin, Microscope, BarChart2, Globe, Loader2 } from 'lucide-react';
import { RovelloLogo } from './components/Header';
import { analyzeMushroom, requestGeolocation } from './utils/mushroomAnalyzer';

const API_URL = process.env.REACT_APP_API_URL || 'https://rovello-backend.onrender.com';
fetch(`${API_URL}/health`).catch(() => {});

const TAB_IDENTIFICA    = 'identifica';
const TAB_DESCOBREIX    = 'descobreix';
const TAB_PILZKONTROLLE = 'pilzkontrolle';
const TAB_DATA          = 'data';

const AppInner = () => {
  const { t, lang } = useT();
  const [activeTab, setActiveTab] = useState(TAB_IDENTIFICA);
  const photosRef = useRef([]);            // [{ file, crop }] (ho manté UploadArea)
  const [photoCount, setPhotoCount] = useState(0);
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [statusText, setStatusText] = useState('');
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

  const handlePhotoCount = (n) => {
    setPhotoCount(n);
    setResult(null);
  };

  const handleAnalyze = async () => {
    const photos = photosRef.current || [];
    if (!photos.length) return;
    setIsAnalyzing(true);
    setResult(null);
    try {
      const context = { month, ...(geo || {}), lang, onStatus: setStatusText };
      const analysis = await analyzeMushroom(photos, context);
      setResult(analysis);
    } catch (e) {
      setResult({ ok: false, error: e?.message || 'unknown' });
    } finally {
      setIsAnalyzing(false);
      setStatusText('');
    }
  };

  const TABS = [
    { key: TAB_IDENTIFICA,    icon: <Search size={20} strokeWidth={1.6} />,     label: t('tabIdentifica') },
    { key: TAB_DESCOBREIX,    icon: <MapPin size={20} strokeWidth={1.6} />,     label: t('tabDescobreix') },
    { key: TAB_PILZKONTROLLE, icon: <Microscope size={20} strokeWidth={1.6} />, label: t('tabPilzkontrolle') },
    { key: TAB_DATA,          icon: <BarChart2 size={20} strokeWidth={1.6} />,  label: t('tabData') },
  ];

  return (
    <div className="min-h-screen bg-cream-50 py-8">
      <div className="max-w-[720px] mx-auto px-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <Header />

          {/* Geo status */}
          <div className="mt-3 text-center text-xs text-muted px-2 leading-relaxed">
            {geoStatus === 'granted' && geo && (
              <p className={geo.byIP ? 'text-amber-700' : 'text-forest-700'}>
                {geo.byIP
                  ? <Globe size={12} className="inline -mt-0.5 mr-1" />
                  : <MapPin size={12} className="inline -mt-0.5 mr-1" />}
                {geo.lat.toFixed(3)}°, {geo.lon.toFixed(3)}° · {geo.byIP ? t('geoByIP') : t('geoActive')}
              </p>
            )}
            {geoStatus === 'denied' && (
              <p className="text-amber-700">
                <MapPin size={12} className="inline -mt-0.5 mr-1" />
                {t('geoDenied')}{' '}
                <button onClick={tryGeolocation}
                  className="underline underline-offset-2 hover:text-amber-900 font-medium">
                  {t('geoRetry')}
                </button>
              </p>
            )}
            {geoStatus === 'requesting' && (
              <p><Loader2 size={12} className="inline -mt-0.5 mr-1 animate-spin" />{t('geoRequesting')}</p>
            )}
          </div>

          {/* Tab bar */}
          <div className="grid grid-cols-4 bg-white rounded-card p-1 mt-5 shadow-sm border border-sage-200">
            {TABS.map(({ key, icon, label }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex flex-col items-center justify-center gap-1 py-2.5 px-1 rounded-btn
                  text-[11px] sm:text-xs font-semibold leading-tight transition-all duration-200
                  ${activeTab === key
                    ? 'bg-forest-900 text-cream-100 shadow-sm'
                    : 'text-muted hover:text-ink'
                  }`}
              >
                <span>{icon}</span>
                <span>{label}</span>
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
                  {geo && <LocalRules geo={geo} />}
                  <UploadArea photosRef={photosRef} onCountChange={handlePhotoCount} />
                  {photoCount > 0 && (
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                      exit={{ y: -20, opacity: 0 }}>
                      <AnalyzeButton onAnalyze={handleAnalyze}
                        isAnalyzing={isAnalyzing} disabled={photoCount === 0} />
                    </motion.div>
                  )}
                  <AnimatePresence mode="wait">
                    <ResultDisplay key={result ? 'result' : 'loading'}
                      result={result} isLoading={isAnalyzing} statusText={statusText} />
                  </AnimatePresence>
                </motion.div>
              )}

              {activeTab === TAB_DESCOBREIX && (
                <motion.div key="descobreix"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
                  <div className="space-y-6">
                    {geo && <LocalRules geo={geo} />}
                    <NearbyMushrooms geo={geo} month={month} />
                  </div>
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
          <span className="inline-flex items-center gap-1.5"><RovelloLogo size={18} /> {t('footerMain')}</span>
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
