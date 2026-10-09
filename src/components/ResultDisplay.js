import React from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle, CheckCircle, HelpCircle, Skull, Leaf, Sprout, Ban,
  Info, MapPin, ShieldAlert, Sparkles, AlertCircle, Images, Lightbulb,
} from 'lucide-react';
import { useT } from '../context/LanguageContext';
import { parseTip } from '../utils/tips';

// Comestibilitat: SEMPRE icona + text + color (mai només el color)
const EDIBILITY = {
  edible:   { Icon: CheckCircle,   cls: 'bg-green-50 text-green-800 border-green-200', dot: 'bg-green-600' },
  toxic:    { Icon: Skull,         cls: 'bg-red-50 text-red-800 border-red-200',       dot: 'bg-alert' },
  caution:  { Icon: AlertTriangle, cls: 'bg-amber-50 text-amber-800 border-amber-200', dot: 'bg-amber-500' },
  inedible: { Icon: Ban,           cls: 'bg-cream-100 text-muted border-sage-200',     dot: 'bg-sage-500' },
  parasite: { Icon: Sprout,        cls: 'bg-cream-100 text-muted border-sage-200',     dot: 'bg-sage-500' },
  lichen:   { Icon: Leaf,          cls: 'bg-cream-100 text-muted border-sage-200',     dot: 'bg-sage-500' },
  unknown:  { Icon: HelpCircle,    cls: 'bg-cream-100 text-muted border-sage-200',     dot: 'bg-sage-500' },
};
const edib = (key) => EDIBILITY[key] || EDIBILITY.unknown;
const pct = (p) => `${Math.round((p || 0) * 100)} %`;
const fill = (s, vars) => Object.entries(vars).reduce((acc, [k, v]) => acc.replace(`{${k}}`, v), s);

// Animació d'escaneig: les làmines radials del logo s'encenen del centre cap enfora
const ScanGills = () => {
  const N = 16;
  return (
    <svg width="76" height="76" viewBox="0 0 100 100" className="mb-4" aria-hidden="true">
      <circle cx="50" cy="50" r="46" fill="none" stroke="#C7D0C5" strokeWidth="1.5" />
      {Array.from({ length: N }).map((_, i) => {
        const a = (i / N) * Math.PI * 2;
        return (
          <motion.line key={i}
            x1={50 + 15 * Math.cos(a)} y1={50 + 15 * Math.sin(a)}
            x2={50 + 40 * Math.cos(a)} y2={50 + 40 * Math.sin(a)}
            stroke="#2E4B3A" strokeWidth="3.5" strokeLinecap="round"
            initial={{ opacity: 0.15 }}
            animate={{ opacity: [0.15, 1, 0.15] }}
            transition={{ duration: 1.6, repeat: Infinity, delay: (i / N) * 1.6, ease: 'easeInOut' }}
          />
        );
      })}
      <circle cx="50" cy="50" r="6.5" fill="#2E4B3A" />
    </svg>
  );
};

// Fila d'un candidat: foto, noms, comestibilitat i barra de probabilitat
const CandidateRow = ({ c, t, withPhoto }) => {
  const e = edib(c.edibility);
  const EIcon = e.Icon;
  return (
    <li className="text-sm">
      <div className="flex items-center gap-2.5">
        {withPhoto && (
          <div className="w-10 h-10 rounded-input overflow-hidden bg-cream-100 border border-sage-200 shrink-0
                          flex items-center justify-center text-sage-500">
            {c.photoUrl
              ? <img src={c.photoUrl} alt="" className="w-full h-full object-cover"
                  onError={(ev) => { ev.currentTarget.style.display = 'none'; }} />
              : <Sprout size={16} strokeWidth={1.5} />}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 min-w-0">
              {!withPhoto && <span className={`w-2 h-2 rounded-pill shrink-0 ${e.dot}`} aria-hidden="true" />}
              <span className="italic text-ink truncate">{c.name}</span>
            </span>
            <span className="text-xs text-muted tabular-nums shrink-0">{pct(c.prob)}</span>
          </div>
          {withPhoto && (
            <div className="flex items-center gap-1.5 text-xs text-muted mt-0.5 min-w-0">
              <EIcon size={12} className="shrink-0" />
              <span className="truncate">
                {t(`edib_${c.edibility}`)}{c.commonName ? ` · ${c.commonName}` : ''}
              </span>
            </div>
          )}
          <div className="mt-1 h-1 rounded-pill bg-cream-100 overflow-hidden">
            <div className="h-full rounded-pill bg-forest-700/60" style={{ width: `${Math.max(2, c.prob * 100)}%` }} />
          </div>
        </div>
      </div>
    </li>
  );
};

const Footer = ({ result, t }) => (
  <div className="mt-4 space-y-1.5">
    {result.zoomFallback && (
      <p className="flex items-start gap-1.5 text-xs text-amber-800">
        <AlertTriangle size={13} className="shrink-0 mt-px" /> {t('zoomFallbackNote')}
      </p>
    )}
    {result.numPhotos > 1 && (
      <p className="flex items-start gap-1.5 text-xs text-forest-700">
        <Images size={13} className="shrink-0 mt-px" /> {fill(t('photosUsed'), { n: result.numPhotos })}
      </p>
    )}
    {result.contextUsed
      ? <p className="flex items-start gap-1.5 text-xs text-forest-700"><Sparkles size={13} className="shrink-0 mt-px" /> {t('contextUsed')}</p>
      : <p className="flex items-start gap-1.5 text-xs text-muted"><MapPin size={13} className="shrink-0 mt-px" /> {t('noContextHint')}</p>}
    <p className="flex items-start gap-1.5 text-xs text-muted">
      <ShieldAlert size={13} className="shrink-0 mt-px" /> {t('safetyLine')}
    </p>
  </div>
);

const ResultDisplay = ({ result, isLoading, statusText }) => {
  const { t } = useT();

  if (isLoading) {
    const waking = statusText && statusText.startsWith('Preparant identificador');
    return (
      <motion.div
        className="bg-white border border-sage-200 rounded-card p-6 text-center flex flex-col items-center"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      >
        <ScanGills />
        <p className="text-ink font-medium mb-1">
          {waking ? t('preparingIdentifier') : t('analyzingTitle')}
        </p>
        <p className="text-muted text-sm">{waking ? t('wakingServer') : t('oneMoment')}</p>
      </motion.div>
    );
  }

  if (!result) return null;

  // ── Error ────────────────────────────────────────────────────────────────
  if (result.ok === false) {
    return (
      <motion.div className="bg-white border border-sage-200 rounded-card p-6"
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-alert shrink-0 mt-0.5" strokeWidth={1.5} />
          <div className="min-w-0">
            <h3 className="text-lg font-semibold text-ink leading-tight">{t('errorTitle')}</h3>
            <p className="text-sm text-muted mt-1 leading-relaxed">
              {t('errorDesc').replace('{detail}', result.error || '?')}
            </p>
            <p className="text-sm text-muted mt-2">{t('errorTip')}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  const cardCls = 'bg-white border border-sage-200 rounded-card p-5 sm:p-6 overflow-hidden';
  const anim = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -12 }, transition: { duration: 0.3 } };

  // ── No n'està segur: candidats en lloc d'una resposta ─────────────────────
  if (result.level === 'unsure') {
    const tips = t('improveTips');
    return (
      <motion.div className={cardCls} {...anim}>
        <div className="flex items-start gap-3">
          <div className="w-11 h-11 rounded-btn bg-amber-50 border border-amber-200 text-amber-700 shrink-0
                          flex items-center justify-center">
            <HelpCircle size={22} strokeWidth={1.6} />
          </div>
          <div className="min-w-0">
            <h3 className="text-lg font-semibold text-ink leading-tight">{t('notSureTitle')}</h3>
            <p className="text-sm text-muted mt-0.5 leading-relaxed">{t('notSureDesc')}</p>
          </div>
        </div>

        {result.genus && result.genus.prob >= 0.4 && (
          <p className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-semibold
                        bg-cream-100 text-forest-700 border border-sage-200">
            <Info size={13} /> {fill(t('genusHint'), { genus: result.genus.genus, pct: pct(result.genus.prob) })}
          </p>
        )}
        {result.anyToxic && (
          <p className="mt-3 flex items-start gap-2 text-sm text-red-800 bg-red-50 border border-red-200 rounded-input p-3">
            <AlertTriangle size={15} className="shrink-0 mt-0.5" /> <span>{t('toxicAmongCandidates')}</span>
          </p>
        )}

        <div className="mt-4">
          <h4 className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">{t('candidatesTitle')}</h4>
          <ul className="space-y-3">
            {(result.candidates || []).map((c) => <CandidateRow key={c.name} c={c} t={t} withPhoto />)}
          </ul>
        </div>

        <div className="mt-5 bg-cream-50 border border-sage-200 p-4 rounded-input">
          <h4 className="flex items-center gap-1.5 text-xs font-semibold text-ink uppercase tracking-wide mb-2">
            <Lightbulb size={13} /> {t('howToImprove')}
          </h4>
          <ul className="space-y-1.5">
            {(Array.isArray(tips) ? tips : []).map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-muted leading-relaxed">
                <span className="shrink-0 w-4 h-4 rounded-pill bg-white border border-sage-200 text-forest-700
                                 text-[10px] font-bold text-center leading-4 mt-0.5">{i + 1}</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
        <Footer result={result} t={t} />
      </motion.div>
    );
  }

  // ── Identificació segura o probable ───────────────────────────────────────
  const e = edib(result.edibility);
  const EdIcon = e.Icon;

  return (
    <motion.div className={cardCls} {...anim}>
      {/* Capçalera: foto de referència + noms + coincidència */}
      <div className="flex items-start gap-3">
        <div className="w-14 h-14 rounded-input overflow-hidden bg-cream-100 border border-sage-200 shrink-0
                        flex items-center justify-center text-sage-500">
          {result.photoUrl
            ? <img src={result.photoUrl} alt="" className="w-full h-full object-cover"
                onError={(ev) => { ev.currentTarget.style.display = 'none'; }} />
            : <Sprout size={22} strokeWidth={1.5} />}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-ink leading-tight italic break-words">{result.name}</h3>
          {result.commonName && (
            <p className="text-sm text-muted mt-0.5 capitalize">{result.commonName}</p>
          )}
        </div>
        <span className="shrink-0 text-xs font-semibold text-forest-700 bg-cream-100 border border-sage-200
                         px-2.5 py-1 rounded-pill whitespace-nowrap tabular-nums">
          {pct(result.confidence)} {t('matchLabel')}
        </span>
      </div>

      {/* Comestibilitat */}
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-semibold border ${e.cls}`}>
          <EdIcon size={14} strokeWidth={2} />
          <span>{t(`edib_${result.edibility}`) || t('edib_unknown')}</span>
        </span>
      </div>

      {/* Probable però no segura */}
      {result.level === 'likely' && (
        <div className="mt-4 flex items-start gap-2.5 bg-amber-50 border border-amber-200 rounded-input p-3">
          <AlertTriangle size={16} className="text-amber-700 shrink-0 mt-0.5" />
          <p className="text-sm text-amber-800 leading-relaxed">{t('likelyNote')}</p>
        </div>
      )}

      {/* Altres candidats */}
      {result.alternatives?.length > 0 && (
        <div className="mt-5">
          <h4 className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">{t('alternativesTitle')}</h4>
          <ul className="space-y-2.5">
            {result.alternatives.map((a) => <CandidateRow key={a.name} c={a} t={t} />)}
          </ul>
        </div>
      )}

      {/* Consells de l'expert */}
      {result.tips?.length > 0 && (
        <div className="mt-5 bg-cream-50 border border-sage-200 p-4 rounded-input">
          <h4 className="text-xs font-semibold text-ink uppercase tracking-wide mb-2">{t('expertTips')}</h4>
          <ul className="space-y-1.5">
            {result.tips.map((tip, i) => {
              const { kind, text } = parseTip(tip);
              const TipIcon = kind === 'warn' ? AlertTriangle : kind === 'plant' ? Sprout : kind === 'lichen' ? Leaf : Info;
              const color = kind === 'warn' ? 'text-alert' : 'text-forest-700';
              return (
                <li key={i} className="flex items-start gap-2 text-sm text-muted leading-relaxed">
                  <TipIcon size={14} className={`${color} shrink-0 mt-1`} />
                  <span>{text}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
      <Footer result={result} t={t} />
    </motion.div>
  );
};

export default ResultDisplay;
