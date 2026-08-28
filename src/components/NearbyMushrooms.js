import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Calendar, RefreshCw, Loader2, AlertTriangle, ChevronDown, ChevronUp, Leaf } from 'lucide-react';
import { useT } from '../context/LanguageContext';
import { MONTHS } from '../i18n/translations';

const API_URL = process.env.REACT_APP_API_URL || 'https://rovello-backend.onrender.com';

const SEASONS = {
  1:'❄️',2:'❄️',3:'🌱',4:'🌱',5:'🌿',6:'☀️',
  7:'☀️',8:'☀️',9:'🍂',10:'🍂',11:'🍂',12:'❄️',
};

// ── Meteorologia (Open-Meteo) ─────────────────────────────────────────────────
const computeActivityScore = (totalRain, avgTemp) => {
  let s = 0;
  if (totalRain >= 5  && totalRain < 10) s += 1;
  else if (totalRain >= 10 && totalRain < 20) s += 2;
  else if (totalRain >= 20 && totalRain < 50) s += 3;
  else if (totalRain >= 50) s += 2;
  if (avgTemp >= 8  && avgTemp <= 22) s += 1;
  if (avgTemp >= 10 && avgTemp <= 18) s += 1;
  return s;
};

const fetchWeather = async (lat, lon) => {
  try {
    const url =
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
      `&daily=precipitation_sum,temperature_2m_max,temperature_2m_min` +
      `&past_days=7&forecast_days=0&timezone=auto`;
    const data = await fetch(url).then(r => r.json());
    const { precipitation_sum, temperature_2m_max, temperature_2m_min } = data.daily;
    const totalRain = precipitation_sum.reduce((a, b) => a + (b || 0), 0);
    const avgMax = temperature_2m_max.reduce((a, b) => a + (b || 0), 0) / temperature_2m_max.length;
    const avgMin = temperature_2m_min.reduce((a, b) => a + (b || 0), 0) / temperature_2m_min.length;
    return {
      totalRain:     Math.round(totalRain * 10) / 10,
      avgMax:        Math.round(avgMax),
      avgMin:        Math.round(avgMin),
      elevation:     Math.round(data.elevation || 0),
      activityScore: computeActivityScore(totalRain, (avgMax + avgMin) / 2),
      rainByDay:     precipitation_sum,
    };
  } catch { return null; }
};

// ── WeatherCard ───────────────────────────────────────────────────────────────
const WeatherCard = ({ weather }) => {
  const { t, lang } = useT();
  if (!weather) return null;

  const getActivityInfo = (score) => {
    if (score >= 4) return { label: t('actExcellent'), emoji: '🟢', color: 'text-forest-700', bg: 'bg-cream-100 border-sage-200' };
    if (score >= 3) return { label: t('actGood'),      emoji: '🟡', color: 'text-forest-700', bg: 'bg-cream-100 border-sage-200' };
    if (score >= 2) return { label: t('actModerate'),  emoji: '🟠', color: 'text-amber-700',  bg: 'bg-amber-50 border-amber-200' };
    return              { label: t('actLow'),       emoji: '🔴', color: 'text-muted',       bg: 'bg-cream-100 border-sage-200' };
  };

  const getTerrainLabel = (elev) => {
    if (elev <= 200)  return t('terrainCoastal');
    if (elev <= 600)  return t('terrainHills');
    if (elev <= 1200) return t('terrainMountain');
    if (elev <= 2000) return t('terrainSubalpine');
    return t('terrainAlpine');
  };

  const act = getActivityInfo(weather.activityScore);
  const maxRain = Math.max(...weather.rainByDay.map(r => r || 0), 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      className={`rounded-card border p-4 ${act.bg}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-ink">{t('terrainCard')}</span>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-pill bg-white ${act.color}`}>
          {act.emoji} {t('activityLabel')} {act.label}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        {[
          { icon: '🌧️', val: `${weather.totalRain} mm`, sub: t('rainLabel') },
          { icon: '🌡️', val: `${weather.avgMin}–${weather.avgMax}°`, sub: t('tempLabel') },
          { icon: '🏔️', val: `${weather.elevation} m`, sub: getTerrainLabel(weather.elevation) },
        ].map(({ icon, val, sub }) => (
          <div key={sub} className="bg-white rounded-btn p-2.5 text-center">
            <div className="text-lg mb-0.5">{icon}</div>
            <div className="text-sm font-bold text-ink">{val}</div>
            <div className="text-xs text-muted leading-tight">{sub}</div>
          </div>
        ))}
      </div>

      {/* Sparkline */}
      <div>
        <div className="flex items-end gap-0.5 h-6">
          {weather.rainByDay.map((rain, i) => {
            const h = Math.max(2, ((rain || 0) / maxRain) * 24);
            return (
              <motion.div key={i} className="flex-1 rounded-sm bg-forest-700"
                initial={{ height: 0 }} animate={{ height: h }}
                transition={{ delay: i * 0.04, duration: 0.3 }}
                title={`${(rain || 0).toFixed(1)} mm`} />
            );
          })}
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-muted">{t('sevenDaysAgo')}</span>
          <span className="text-xs text-muted">{t('todayLabel')}</span>
        </div>
      </div>
    </motion.div>
  );
};

// ── SpeciesCard (top 5) ───────────────────────────────────────────────────────
const SpeciesCard = ({ species, probability, maxProb, rank, info }) => {
  const { t } = useT();
  const [showTips, setShowTips] = useState(false);
  const relPct = (probability / maxProb) * 100;
  const tips   = info?.tips || [];

  const edibLabel = info?.edibility ? t(`edib_${info.edibility}`) : t('edib_unknown');
  const edibCls = {
    edible:   'bg-green-50 text-green-800 border-green-200',
    toxic:    'bg-red-50 text-red-800 border-red-200',
    caution:  'bg-amber-50 text-amber-800 border-amber-200',
    inedible: 'bg-cream-100 text-muted border-sage-200',
    parasite: 'bg-cream-100 text-muted border-sage-200',
    lichen:   'bg-cream-100 text-muted border-sage-200',
    unknown:  'bg-cream-100 text-muted border-sage-200',
  }[info?.edibility || 'unknown'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.06, duration: 0.3 }}
      className="bg-white rounded-card border border-sage-200 shadow-sm hover:shadow-sm
                 hover:border-sage-200 transition-all overflow-hidden"
    >
      <div className="flex">
        <div className="w-20 h-20 shrink-0 bg-cream-100 relative overflow-hidden">
          {info?.photo_url ? (
            <img src={info.photo_url} alt={species} className="w-full h-full object-cover"
              onError={e => { e.target.style.display = 'none'; }} />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-2xl">🍄</div>
          )}
          <div className="absolute top-1 left-1 bg-black/50 text-white text-xs font-bold
                          w-5 h-5 rounded-pill flex items-center justify-center">{rank + 1}</div>
        </div>
        <div className="flex-1 px-3 py-2.5 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div className="min-w-0">
              <p className="text-sm font-semibold text-ink italic truncate leading-tight">{species}</p>
              {info?.common_name && <p className="text-xs text-muted truncate mt-0.5">{info.common_name}</p>}
            </div>
            <span className={`shrink-0 text-xs px-2 py-0.5 rounded-pill border font-medium whitespace-nowrap ${edibCls}`}>
              {edibLabel}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 bg-cream-100 rounded-pill h-1.5 overflow-hidden">
              <motion.div className="h-1.5 rounded-pill bg-forest-700"
                initial={{ width: 0 }} animate={{ width: `${relPct}%` }}
                transition={{ delay: rank * 0.06 + 0.15, duration: 0.6, ease: 'easeOut' }} />
            </div>
            <span className="text-xs text-muted font-mono w-12 text-right shrink-0">
              {(probability * 100).toFixed(3)}%
            </span>
          </div>
        </div>
      </div>

      {tips.length > 0 && (
        <div className="border-t border-sage-200">
          <button onClick={() => setShowTips(v => !v)}
            className="w-full flex items-center justify-between px-3 py-2 text-xs
                       text-forest-700 hover:bg-cream-100 transition-colors">
            <span className="font-semibold">
              🔎 {t('howToId')} ({tips.length} {t('tipsWord')})
            </span>
            {showTips ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
          <AnimatePresence>
            {showTips && (
              <motion.div
                initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <ol className="px-3 pb-3 space-y-2">
                  {tips.map((tip, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-muted leading-relaxed">
                      <span className="shrink-0 w-4 h-4 rounded-pill bg-cream-100 text-forest-700
                                       font-bold text-center leading-4 mt-0.5">{i + 1}</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ol>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
};

// ── SpeciesRow (rang 6-25) ────────────────────────────────────────────────────
const SpeciesRow = ({ species, probability, maxProb, rank, tier, info }) => {
  const { t } = useT();
  const relPct   = (probability / maxProb) * 100;
  const edib     = info?.edibility;
  const barColor = tier === 'mid' ? 'bg-forest-700' : 'bg-sage-200';
  const badge    = tier === 'mid'
    ? { text: t('rowGood'),     cls: 'bg-cream-100 text-forest-700' }
    : { text: t('rowPossible'), cls: 'bg-cream-100 text-muted' };

  const edibDot = edib === 'edible'   ? 'bg-green-500'
                : edib === 'toxic'    ? 'bg-red-500'
                : edib === 'caution'  ? 'bg-amber-500'
                : edib === 'parasite' ? 'bg-sage-200'
                : edib === 'lichen'   ? 'bg-sage-200'
                : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}
      transition={{ delay: rank * 0.02, duration: 0.2 }}
      className="bg-white rounded-btn px-4 py-2.5 border border-sage-200 shadow-sm
                 hover:border-sage-200 transition-all"
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-muted text-xs font-mono w-5 shrink-0">
            {String(rank + 1).padStart(2, '0')}
          </span>
          {edibDot && <span className={`shrink-0 w-2 h-2 rounded-pill ${edibDot}`} title={edib} />}
          <span className="text-sm text-ink italic truncate">{species}</span>
        </div>
        <span className={`shrink-0 text-xs px-2 py-0.5 rounded-pill font-medium ml-2 ${badge.cls}`}>
          {badge.text}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-cream-100 rounded-pill h-1.5 overflow-hidden">
          <motion.div className={`h-1.5 rounded-pill ${barColor}`}
            initial={{ width: 0 }} animate={{ width: `${relPct}%` }}
            transition={{ delay: rank * 0.02 + 0.1, duration: 0.4, ease: 'easeOut' }} />
        </div>
        <span className="text-xs text-muted font-mono w-12 text-right shrink-0">
          {(probability * 100).toFixed(3)}%
        </span>
      </div>
    </motion.div>
  );
};

// ── Component principal ───────────────────────────────────────────────────────

const NearbyMushrooms = ({ geo, month }) => {
  const { t, lang } = useT();
  const [forecast,     setForecast]     = useState(null);
  const [speciesInfo,  setSpeciesInfo]  = useState({});
  const [weather,      setWeather]      = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [loadingInfo,  setLoadingInfo]  = useState(false);
  const [error,        setError]        = useState(null);
  const [filterEdible, setFilterEdible] = useState(false);
  const [waking,       setWaking]       = useState(false);

  useEffect(() => {
    if (!geo) return;
    fetchWeather(geo.lat, geo.lon).then(setWeather);
  }, [geo]);

  const loadForecast = useCallback(async () => {
    if (!geo) return;
    setLoading(true); setError(null); setSpeciesInfo({}); setWaking(false);

    const doFetch = () => fetch(`${API_URL}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat: geo.lat, lon: geo.lon, month, k: 25 }),
    });

    let res;
    try {
      res = await doFetch();
    } catch {
      // Primer intent fallat → servidor adormit, esperem 35s i reintenten
      setWaking(true);
      await new Promise(r => setTimeout(r, 35000));
      setWaking(false);
      try {
        res = await doFetch();
      } catch (e2) {
        setError(e2.message); setLoading(false); return;
      }
    }

    if (!res.ok) {
      setError(`Error ${res.status}`); setLoading(false); return;
    }
    const data = await res.json();
    setForecast(data);
    setLoading(false);

    const allSp = data.forecast.map(f => f.species);
    setLoadingInfo(true);
    fetch(`${API_URL}/species-info`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ species: allSp.slice(0, 8) }),
    })
      .then(r => r.json())
      .then(info => {
        setSpeciesInfo(prev => ({ ...prev, ...info }));
        const rest = allSp.slice(8);
        if (!rest.length) { setLoadingInfo(false); return; }
        return fetch(`${API_URL}/species-info`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ species: rest }),
        }).then(r => r.json()).then(i2 => setSpeciesInfo(prev => ({ ...prev, ...i2 })));
      })
      .catch(() => {})
      .finally(() => setLoadingInfo(false));
  }, [geo, month]);

  useEffect(() => { loadForecast(); }, [loadForecast]);

  if (!geo) {
    return (
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
        className="bg-amber-50 border border-amber-200 rounded-card p-8 text-center">
        <div className="text-4xl mb-3">📍</div>
        <p className="text-amber-800 font-semibold">{t('nearbyNoGeoTitle')}</p>
        <p className="text-amber-600 text-sm mt-2 leading-relaxed">{t('nearbyNoGeoDesc')}</p>
      </motion.div>
    );
  }

  const maxProb = forecast?.forecast?.[0]?.probability || 1;
  const applyFilter = (items) => {
    if (!filterEdible) return items;
    return items.filter(item => speciesInfo[item.species]?.edibility === 'edible');
  };
  const highTier = applyFilter(forecast?.forecast?.slice(0, 5)  || []);
  const midTier  = applyFilter(forecast?.forecast?.slice(5, 13) || []);
  const lowTier  = applyFilter(forecast?.forecast?.slice(13)    || []);
  const total    = highTier.length + midTier.length + lowTier.length;
  const hasRes   = forecast && !loading;
  const monthName = MONTHS[lang][month - 1];

  return (
    <div className="space-y-4">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
        className="bg-forest-900 rounded-card p-4 text-cream-100 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-cream-100 text-xs font-medium uppercase tracking-wide mb-1">
              {t('nearbyTitle')}
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <span className="flex items-center gap-1.5 text-sm font-medium">
                <Calendar size={13} /> {SEASONS[month]} {monthName}
              </span>
              <span className="flex items-center gap-1.5 text-sm font-medium">
                <MapPin size={13} /> {geo.lat.toFixed(2)}°N, {geo.lon.toFixed(2)}°E
              </span>
            </div>
          </div>
          <button onClick={loadForecast} disabled={loading}
            className="p-2.5 bg-forest-700 rounded-btn hover:bg-forest-700 transition-colors">
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </motion.div>

      <WeatherCard weather={weather} />

      {/* Filtre */}
      {hasRes && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2">
          <button onClick={() => setFilterEdible(v => !v)}
            className={`flex items-center gap-2 px-4 py-2 rounded-btn text-sm font-semibold
                        border transition-all duration-200
                        ${filterEdible
                          ? 'bg-forest-900 text-cream-100 border-forest-900 shadow-sm'
                          : 'bg-white text-muted border-sage-200 hover:border-sage-200 hover:text-forest-700'}`}>
            <Leaf size={14} />
            {t('filterEdibleBtn')}
            {filterEdible && total > 0 && (
              <span className="bg-forest-700 text-cream-100 text-xs px-1.5 py-0.5 rounded-pill font-bold">
                {total}
              </span>
            )}
          </button>
          {filterEdible && loadingInfo && (
            <span className="flex items-center gap-1.5 text-xs text-muted">
              <Loader2 size={11} className="animate-spin" /> {t('filterLoading')}
            </span>
          )}
          {filterEdible && !loadingInfo && total === 0 && (
            <span className="text-xs text-amber-500">{t('filterNoResults')}</span>
          )}
        </motion.div>
      )}

      <AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center py-14 gap-3">
            <Loader2 size={34} className="animate-spin text-forest-700" />
            <p className="text-muted text-sm">
              {waking ? '⏳ Despertant servidor... (fins 30 seg)' : t('nearbyLoading')}
            </p>
            {waking && (
              <p className="text-muted text-xs text-center max-w-[220px] leading-relaxed">
                El servidor gratuït adorm quan no s'usa. Només triga la primera vegada.
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {error && !loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-btn p-4">
          <AlertTriangle size={18} className="text-red-500 mt-0.5 shrink-0" />
          <div>
            <p className="text-red-700 font-medium text-sm">{t('nearbyError')}</p>
            <p className="text-red-500 text-xs mt-0.5">{error}</p>
          </div>
        </motion.div>
      )}

      {hasRes && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          <p className="text-xs text-muted text-center">
            {filterEdible
              ? `${total} ${t('nearbyEdibleAmong')} ${forecast.forecast.length}`
              : `Top ${forecast.forecast.length} ${t('nearbyOf')} ${forecast.total_species.toLocaleString()} ${t('nearbySpecies')}`
            }
            {' '}· {t('nearbyObs')} · {monthName}
          </p>

          {/* Mode filtre: totes les comestibles com a SpeciesCard amb foto i tips */}
          {filterEdible ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 rounded-pill bg-forest-900 inline-block" />
                <span className="text-xs font-semibold text-forest-700 uppercase tracking-wide">
                  ✅ {t('edib_edible')}
                </span>
                {loadingInfo && <Loader2 size={11} className="animate-spin text-muted" />}
              </div>
              {[...highTier, ...midTier, ...lowTier].map((item, i) => (
                <SpeciesCard key={item.species} species={item.species}
                  probability={item.probability} maxProb={maxProb}
                  rank={i} info={speciesInfo[item.species]} />
              ))}
            </div>
          ) : (
            <>
              {highTier.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-pill bg-forest-900 inline-block" />
                    <span className="text-xs font-semibold text-forest-700 uppercase tracking-wide">
                      {t('highProbLabel')}
                    </span>
                    {loadingInfo && <Loader2 size={11} className="animate-spin text-muted" />}
                  </div>
                  <div className="space-y-2">
                    {highTier.map((item, i) => (
                      <SpeciesCard key={item.species} species={item.species}
                        probability={item.probability} maxProb={maxProb}
                        rank={i} info={speciesInfo[item.species]} />
                    ))}
                  </div>
                </div>
              )}

              {midTier.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-pill bg-sage-200 inline-block" />
                    <span className="text-xs font-semibold text-forest-700 uppercase tracking-wide">
                      {t('goodProbLabel')}
                    </span>
                  </div>
                  <div className="space-y-1.5">
                    {midTier.map((item, i) => (
                      <SpeciesRow key={item.species} species={item.species}
                        probability={item.probability} maxProb={maxProb}
                        rank={i + 5} tier="mid" info={speciesInfo[item.species]} />
                    ))}
                  </div>
                </div>
              )}

              {lowTier.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-pill bg-sage-200 inline-block" />
                    <span className="text-xs font-semibold text-muted uppercase tracking-wide">
                      {t('possibleLabel')}
                    </span>
                  </div>
                  <div className="space-y-1.5">
                    {lowTier.map((item, i) => (
                      <SpeciesRow key={item.species} species={item.species}
                        probability={item.probability} maxProb={maxProb}
                        rank={i + 13} tier="low" info={speciesInfo[item.species]} />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {filterEdible && total === 0 && !loadingInfo && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="text-center py-8 text-muted">
              <div className="text-3xl mb-2">🍄</div>
              <p className="text-sm font-medium text-muted">{t('filterNoResults')}</p>
              <button onClick={() => setFilterEdible(false)}
                className="mt-3 text-xs text-forest-700 underline">{t('filterShowAll')}</button>
            </motion.div>
          )}

          <p className="text-xs text-muted text-center pt-1 leading-relaxed">
            {t('nearbyDisclaimer')}
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default NearbyMushrooms;
