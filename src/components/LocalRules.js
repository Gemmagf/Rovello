import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Landmark, Scale, CalendarX, CalendarCheck, Moon, ShieldAlert, ExternalLink,
  ChevronDown, ChevronUp, Loader2, Info,
} from 'lucide-react';
import { useT } from '../context/LanguageContext';
import { getRulesFor } from '../data/pickingRules';

// ── Geocodificació inversa (OpenStreetMap Nominatim) amb memòria cau ─────────
const memCache = {};
const reverseGeocode = async (lat, lon, lang) => {
  const key = `${lat.toFixed(2)},${lon.toFixed(2)},${lang}`;
  if (memCache[key]) return memCache[key];
  try {
    const saved = JSON.parse(localStorage.getItem(`rovello_region_${key}`) || 'null');
    if (saved && Date.now() - saved.ts < 30 * 864e5) { memCache[key] = saved.v; return saved.v; }
  } catch {}
  const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&zoom=8&accept-language=${lang}`;
  const r = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!r.ok) throw new Error(`geocode ${r.status}`);
  const d = await r.json();
  const a = d.address || {};
  const v = {
    country: (a.country_code || '').toUpperCase(),
    region: a['ISO3166-2-lvl4'] || '',
    regionName: a.state || a.county || a.region || '',
  };
  memCache[key] = v;
  try { localStorage.setItem(`rovello_region_${key}`, JSON.stringify({ ts: Date.now(), v })); } catch {}
  return v;
};

const fill = (s, vars) => Object.entries(vars).reduce((acc, [k, v]) => acc.replace(`{${k}}`, v), s);

const LocalRules = ({ geo }) => {
  const { t, lang } = useT();
  const [state, setState] = useState({ loading: true });
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let alive = true;
    if (!geo) return undefined;
    setState({ loading: true });
    reverseGeocode(geo.lat, geo.lon, lang)
      .then((loc) => { if (alive) setState({ loading: false, loc, ...getRulesFor(loc.country, loc.region) }); })
      .catch(() => { if (alive) setState({ loading: false, error: true }); });
    return () => { alive = false; };
  }, [geo, lang]);

  if (!geo) return null;

  if (state.loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted px-1">
        <Loader2 size={13} className="animate-spin" /> {t('rulesLoading')}
      </div>
    );
  }
  if (state.error || !state.kind) return null; // fora de Suïssa/Catalunya: no mostrem res

  const { rules, loc, kind } = state;
  const today = new Date().getDate();
  const closed = rules.closedDays && today >= rules.closedDays[0] && today <= rules.closedDays[1];
  const regionLabel = kind === 'ch-canton' || kind === 'ch-general'
    ? fill(t('rulesRegionCanton'), { name: loc.regionName || 'CH' })
    : (loc.regionName || 'Catalunya');
  const note = rules.notes && (rules.notes[lang] || rules.notes.ca);
  const L = (o) => (o && typeof o === 'object' ? (o[lang] || o.ca) : o);
  // Cantó sense cap restricció pròpia → s'apliquen les normes generals suïsses
  const isGeneral = kind === 'ch-general'
    || (kind === 'ch-canton' && !rules.closedDays && !rules.maxKg && !rules.night && !rules.notes && !rules.communal);

  const rows = [];
  if (rules.closedDays) {
    rows.push({ Icon: CalendarX, text: fill(t('rulesClosedDays'), { a: rules.closedDays[0], b: rules.closedDays[1] }) });
  } else if (kind !== 'es-ct') {
    rows.push({ Icon: CalendarCheck, text: t('rulesNoClosedDays') });
  }
  if (rules.maxKg) {
    let txt = fill(t('rulesMaxKg'), { kg: rules.maxKg });
    if (rules.limits?.length) txt += ` (${rules.limits.map((l) => `${L(l.what)}: ${l.kg} kg`).join(', ')})`;
    rows.push({ Icon: Scale, text: txt });
  } else if (kind !== 'es-ct') {
    rows.push({ Icon: Scale, text: t('rulesNoLimit') });
  }
  if (rules.night) rows.push({ Icon: Moon, text: fill(t('rulesNight'), { from: rules.night.from, to: rules.night.to }) });
  if (rules.reserves) rows.push({ Icon: ShieldAlert, text: t('rulesReserves') });

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-sage-200 rounded-card p-4 sm:p-5"
      aria-label={t('rulesTitle')}
    >
      <button type="button" onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-3 text-left">
        <span className="flex items-center gap-2.5 min-w-0">
          <span className="w-9 h-9 rounded-btn bg-cream-100 border border-sage-200 flex items-center justify-center
                           text-forest-700 shrink-0">
            <Landmark size={18} strokeWidth={1.6} />
          </span>
          <span className="min-w-0">
            <span className="block text-[11px] font-semibold text-muted uppercase tracking-wide">{t('rulesTitle')}</span>
            <span className="block text-sm font-semibold text-ink truncate">{regionLabel}</span>
          </span>
        </span>
        <span className="flex items-center gap-2 shrink-0">
          {rules.closedDays && (
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-pill text-[11px] font-semibold border ${
              closed ? 'bg-red-50 text-red-800 border-red-200' : 'bg-green-50 text-green-800 border-green-200'}`}>
              {closed ? <CalendarX size={12} /> : <CalendarCheck size={12} />}
              <span className="hidden sm:inline">{closed ? t('rulesTodayClosed') : t('rulesTodayOk')}</span>
            </span>
          )}
          {open ? <ChevronUp size={16} className="text-muted" /> : <ChevronDown size={16} className="text-muted" />}
        </span>
      </button>

      {/* Resum sempre visible: estat d'avui + límit */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {rules.closedDays && (
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-pill text-xs font-medium border sm:hidden ${
            closed ? 'bg-red-50 text-red-800 border-red-200' : 'bg-green-50 text-green-800 border-green-200'}`}>
            {closed ? <CalendarX size={12} /> : <CalendarCheck size={12} />}
            {closed ? t('rulesTodayClosed') : t('rulesTodayOk')}
          </span>
        )}
        {closed && (
          <span className="inline-flex items-center px-2.5 py-1 rounded-pill text-xs text-muted bg-cream-100 border border-sage-200">
            {fill(t('rulesClosedUntil'), { d: rules.closedDays[1] + 1 })}
          </span>
        )}
        {rules.maxKg && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-pill text-xs text-forest-700 bg-cream-100 border border-sage-200">
            <Scale size={12} /> {fill(t('rulesMaxKg'), { kg: rules.maxKg })}
          </span>
        )}
        {isGeneral && !open && (
          <span className="text-xs text-muted">{t('rulesGeneralCH')}</span>
        )}
      </div>

      {open && (
        <div className="mt-4 space-y-2.5">
          {isGeneral && (
            <p className="text-sm text-muted leading-relaxed">{t('rulesGeneralCH')}</p>
          )}
          <ul className="space-y-2">
            {rows.map(({ Icon, text }) => (
              <li key={text} className="flex items-start gap-2.5 text-sm text-ink">
                <Icon size={15} className="text-forest-700 shrink-0 mt-0.5" strokeWidth={1.8} />
                <span>{text}</span>
              </li>
            ))}
          </ul>
          {note && (
            <p className="flex items-start gap-2 text-sm text-muted leading-relaxed bg-cream-50 border border-sage-200 rounded-input p-3">
              <Info size={14} className="text-forest-700 shrink-0 mt-0.5" /> <span>{note}</span>
            </p>
          )}
          <p className="text-xs text-muted leading-relaxed">{t('rulesDisclaimer')}</p>
          {rules.source && (
            <a href={rules.source} target="_blank" rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs font-medium text-forest-700 underline underline-offset-2">
              <ExternalLink size={12} /> {t('rulesSource')}{rules.updated ? ` · ${t('rulesUpdated')} ${rules.updated}` : ''}
            </a>
          )}
        </div>
      )}
      {!open && (
        <button type="button" onClick={() => setOpen(true)}
          className="mt-2 text-xs font-medium text-forest-700 underline underline-offset-2">
          {t('rulesShowMore')}
        </button>
      )}
    </motion.section>
  );
};

export default LocalRules;
