import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, ExternalLink, Phone, AlertTriangle } from 'lucide-react';
import { useT } from '../context/LanguageContext';

const CANTONS = [
  { abbr:'AG', name:'Aargau',               lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'AI', name:'Appenzell Innerrhoden', lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'AR', name:'Appenzell Ausserrhoden',lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'BE', name:'Bern / Berne',          lang:'de/fr', url:'https://www.vsvp.ch' },
  { abbr:'BL', name:'Basel-Landschaft',      lang:'de',    url:'https://www.baselland.ch' },
  { abbr:'BS', name:'Basel-Stadt',           lang:'de',    url:'https://www.gesundheit.bs.ch' },
  { abbr:'FR', name:'Fribourg / Freiburg',   lang:'fr/de', url:'https://www.fr.ch/saav' },
  { abbr:'GE', name:'Genève',                lang:'fr',    url:'https://www.ge.ch/scav' },
  { abbr:'GL', name:'Glarus',                lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'GR', name:'Graubünden / Grischun', lang:'de/rm/it', url:'https://www.gr.ch' },
  { abbr:'JU', name:'Jura',                  lang:'fr',    url:'https://www.jura.ch' },
  { abbr:'LU', name:'Luzern',                lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'NE', name:'Neuchâtel',             lang:'fr',    url:'https://www.ne.ch' },
  { abbr:'NW', name:'Nidwalden',             lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'OW', name:'Obwalden',              lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'SG', name:'St. Gallen',            lang:'de',    url:'https://www.sg.ch' },
  { abbr:'SH', name:'Schaffhausen',          lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'SO', name:'Solothurn',             lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'SZ', name:'Schwyz',                lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'TG', name:'Thurgau',               lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'TI', name:'Ticino',                lang:'it',    url:'https://www.ti.ch/veterinario' },
  { abbr:'UR', name:'Uri',                   lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'VD', name:'Vaud',                  lang:'fr',    url:'https://www.vd.ch/scav' },
  { abbr:'VS', name:'Valais / Wallis',       lang:'fr/de', url:'https://www.vs.ch/web/sca' },
  { abbr:'ZG', name:'Zug',                   lang:'de',    url:'https://www.vsvp.ch' },
  { abbr:'ZH', name:'Zürich',                lang:'de',    url:'https://www.stadtforstamt.ch', highlight: true },
];

const LANG_FLAG = {
  de:'🇩🇪', fr:'🇫🇷', it:'🇮🇹', rm:'🗺️',
  'de/fr':'🇩🇪🇫🇷','fr/de':'🇫🇷🇩🇪','de/rm/it':'🇩🇪🇮🇹','fr/it':'🇫🇷🇮🇹',
};

const PilzkontrolleInfo = () => {
  const { t } = useT();
  const [query, setQuery] = useState('');

  const filtered = CANTONS.filter(c =>
    c.name.toLowerCase().includes(query.toLowerCase()) ||
    c.abbr.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Emergència */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
        className="bg-red-600 rounded-card p-4 text-white shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-white/20 rounded-btn shrink-0"><Phone size={20} /></div>
          <div>
            <p className="text-red-100 text-xs font-medium uppercase tracking-wide mb-0.5">
              {t('pilzEmergency')}
            </p>
            <p className="text-2xl font-black tracking-wide">145</p>
            <p className="text-red-100 text-xs mt-0.5">{t('pilzToxcentre')}</p>
          </div>
        </div>
      </motion.div>

      {/* Avís */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
        className="bg-amber-50 border border-amber-200 rounded-card p-3 flex items-start gap-2.5">
        <AlertTriangle size={15} className="text-amber-500 mt-0.5 shrink-0" />
        <p className="text-amber-700 text-xs leading-relaxed">{t('pilzWarning')}</p>
      </motion.div>

      {/* Directori VSVP */}
      <motion.a href="https://www.vsvp.ch" target="_blank" rel="noopener noreferrer"
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
        className="block bg-forest-900 rounded-card p-4
                   text-cream-100 shadow-sm hover:shadow-sm transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-cream-100 text-xs font-medium uppercase tracking-wide mb-1">
              {t('pilzDirTitle')}
            </p>
            <p className="text-xl font-bold">vsvp.ch</p>
            <p className="text-cream-100 text-sm mt-0.5">{t('pilzDirCTA')}</p>
          </div>
          <ExternalLink size={20} className="opacity-70 shrink-0" />
        </div>
      </motion.a>

      {/* Cerca */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
        className="relative">
        <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" />
        <input
          type="text"
          placeholder={t('pilzSearchPlaceholder')}
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 text-sm border border-sage-200 rounded-btn
                     focus:outline-none focus:border-forest-700 focus:ring-2 focus:ring-cream-100
                     bg-white placeholder:text-muted"
        />
      </motion.div>

      {/* Llista cantons */}
      <div className="space-y-2">
        {filtered.map((c, i) => (
          <motion.div key={c.abbr}
            initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.02, duration: 0.2 }}
            className={`bg-white rounded-btn border shadow-sm overflow-hidden
                        ${c.highlight ? 'border-forest-900' : 'border-sage-200'}`}>
            <div className="flex items-center gap-3 p-3">
              <div className={`shrink-0 w-10 h-10 rounded-input flex items-center justify-center
                              text-xs font-black text-white bg-forest-900`}>
                {c.abbr}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="text-sm font-semibold text-ink">{c.name}</span>
                  <span className="text-xs">{LANG_FLAG[c.lang] || ''}</span>
                  {c.highlight && (
                    <span className="text-xs bg-cream-100 text-forest-700 px-1.5 py-0.5
                                     rounded-pill font-medium">
                      {t('pilzPermanent')}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted">{c.url.replace('https://', '')}</p>
              </div>
              <a href={c.url} target="_blank" rel="noopener noreferrer"
                className="shrink-0 p-2 text-muted hover:text-forest-700 hover:bg-cream-100
                           rounded-input transition-colors">
                <ExternalLink size={14} />
              </a>
            </div>
          </motion.div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-8 text-muted text-sm">{t('pilzNoCanton')}</div>
        )}
      </div>

      {/* Consells */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
        className="bg-cream-50 rounded-card p-4 space-y-2.5">
        <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
          🍄 {t('pilzTipsTitle')}
        </p>
        {t('pilzTips').map(([icon, text]) => (
          <div key={text} className="flex items-start gap-2.5">
            <span className="text-base shrink-0 mt-0.5">{icon}</span>
            <p className="text-xs text-muted leading-relaxed">{text}</p>
          </div>
        ))}
      </motion.div>

      <p className="text-xs text-muted text-center pb-2 leading-relaxed">
        VSVP · Verband Schweizerischer Pilzfachleute ·{' '}
        <a href="https://www.vsvp.ch" target="_blank" rel="noopener noreferrer"
          className="underline hover:text-forest-700">vsvp.ch</a>
      </p>
    </div>
  );
};

export default PilzkontrolleInfo;
