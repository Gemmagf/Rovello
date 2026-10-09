import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ZoomIn, ZoomOut } from 'lucide-react';
import { useT } from '../context/LanguageContext';

const MAX_ZOOM = 8;

/**
 * Enquadrador quadrat: l'usuari arrossega i fa zoom (pessic, roda o lliscador)
 * perquè el bolet ompli el marc. Notifica el retall en coordenades normalitzades
 * de la imatge original ({x, y, w, h} entre 0 i 1), que després es retalla de la
 * foto a resolució completa abans d'enviar-la al model.
 */
const PhotoCropper = ({ src, onCropChange }) => {
  const { t } = useT();
  const boxRef = useRef(null);
  const [nat, setNat] = useState(null);            // mida natural de la imatge
  const [side, setSide] = useState(0);             // costat del marc (px)
  const [view, setView] = useState({ z: 1, tx: 0, ty: 0 });
  const pointers = useRef(new Map());

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return undefined;
    const update = () => setSide(el.clientWidth);
    update();
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(update) : null;
    if (ro) ro.observe(el);
    return () => ro && ro.disconnect();
  }, []);

  const base = nat && side ? side / Math.min(nat.w, nat.h) : 0;   // escala «cover»

  const clamp = useCallback((v) => {
    if (!nat || !side) return v;
    const z = Math.min(MAX_ZOOM, Math.max(1, v.z));
    const dw = nat.w * base * z, dh = nat.h * base * z;
    return { z, tx: Math.min(0, Math.max(side - dw, v.tx)), ty: Math.min(0, Math.max(side - dh, v.ty)) };
  }, [nat, side, base]);

  // Vista inicial: imatge centrada cobrint el marc. Si el marc canvia de mida
  // (o es torna a mostrar després d'estar amagat) es conserva l'enquadrament.
  const inited = useRef(false);
  const lastSide = useRef(0);
  useEffect(() => {
    if (!nat || !side) return;
    if (!inited.current) {
      setView({ z: 1, tx: (side - nat.w * base) / 2, ty: (side - nat.h * base) / 2 });
      inited.current = true;
    } else if (lastSide.current && lastSide.current !== side) {
      const r = side / lastSide.current;
      setView((v) => clamp({ z: v.z, tx: v.tx * r, ty: v.ty * r }));
    }
    lastSide.current = side;
  }, [nat, side, base]); // eslint-disable-line

  // Notifica el retall actual (normalitzat respecte de la imatge original)
  useEffect(() => {
    if (!nat || !side || !onCropChange) return;
    const k = base * view.z;
    const size = side / k;
    onCropChange({ x: (-view.tx / k) / nat.w, y: (-view.ty / k) / nat.h, w: size / nat.w, h: size / nat.h, zoom: view.z });
  }, [view, nat, side, base]); // eslint-disable-line

  const zoomAt = useCallback((px, py, factor) => {
    setView((v) => {
      const z = Math.min(MAX_ZOOM, Math.max(1, v.z * factor));
      const r = z / v.z;
      return clamp({ z, tx: px - (px - v.tx) * r, ty: py - (py - v.ty) * r });
    });
  }, [clamp]);

  const local = (e) => {
    const r = boxRef.current.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  const onPointerDown = (e) => {
    try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* punter sintètic o no capturable */ }
    pointers.current.set(e.pointerId, local(e));
  };
  const onPointerMove = (e) => {
    const prev = pointers.current.get(e.pointerId);
    if (!prev) return;
    const cur = local(e);
    if (pointers.current.size === 1) {
      const dx = cur.x - prev.x, dy = cur.y - prev.y;
      setView((v) => clamp({ ...v, tx: v.tx + dx, ty: v.ty + dy }));
    } else if (pointers.current.size === 2) {
      const other = [...pointers.current.entries()].find(([id]) => id !== e.pointerId)[1];
      const d0 = Math.hypot(prev.x - other.x, prev.y - other.y) || 1;
      const d1 = Math.hypot(cur.x - other.x, cur.y - other.y) || 1;
      zoomAt((cur.x + other.x) / 2, (cur.y + other.y) / 2, d1 / d0);
    }
    pointers.current.set(e.pointerId, cur);
  };
  const onPointerEnd = (e) => { pointers.current.delete(e.pointerId); };

  // Roda del ratolí (listener natiu no passiu per poder fer preventDefault)
  useEffect(() => {
    const el = boxRef.current;
    if (!el) return undefined;
    const onWheel = (e) => {
      e.preventDefault();
      const r = el.getBoundingClientRect();
      zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.0015));
    };
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWheel);
  }, [zoomAt]);

  const ready = nat && side;
  return (
    <div className="w-full flex flex-col items-center">
      <div
        ref={boxRef}
        className="relative w-full max-w-[340px] aspect-square overflow-hidden rounded-card border border-sage-200
                   bg-cream-100 touch-none select-none cursor-grab active:cursor-grabbing"
        onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerEnd} onPointerCancel={onPointerEnd} onPointerLeave={onPointerEnd}
        role="img" aria-label={t('cropHint')}
      >
        <img
          src={src} alt="" draggable={false}
          onLoad={(e) => setNat({ w: e.target.naturalWidth, h: e.target.naturalHeight })}
          style={ready
            ? { position: 'absolute', left: view.tx, top: view.ty, width: nat.w * base * view.z, height: nat.h * base * view.z, maxWidth: 'none' }
            : { opacity: 0 }}
        />
        {/* Guia: el bolet hauria d'omplir el cercle */}
        <div className="pointer-events-none absolute inset-[9%] rounded-full border-2 border-dashed border-white/70"
             style={{ boxShadow: '0 0 0 1px rgba(35,53,43,0.25)' }} />
      </div>

      <div className="w-full max-w-[340px] mt-3 flex items-center gap-2.5 text-forest-700">
        <ZoomOut size={16} strokeWidth={1.6} className="shrink-0" />
        <input
          type="range" min="1" max={MAX_ZOOM} step="0.01" value={view.z}
          onChange={(e) => zoomAt(side / 2, side / 2, parseFloat(e.target.value) / view.z)}
          className="w-full accent-forest-900" aria-label="Zoom"
        />
        <ZoomIn size={16} strokeWidth={1.6} className="shrink-0" />
      </div>
      <p className="mt-2 text-xs text-muted leading-relaxed max-w-[340px]">{t('cropHint')}</p>
    </div>
  );
};

export default PhotoCropper;
