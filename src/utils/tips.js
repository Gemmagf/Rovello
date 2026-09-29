/**
 * Els consells del backend porten un prefix semàntic (⚠️ perill, 🌱 paràsit de
 * plantes, 🪨 liquen). La UI no mostra emojis: aquí es converteixen en un tipus
 * d'icona i es retorna el text net.
 */
const PREFIXES = [
  ['⚠️', 'warn'], ['⚠', 'warn'], ['☠️', 'warn'], ['🌱', 'plant'], ['🪨', 'lichen'],
];

export const parseTip = (tip) => {
  let text = String(tip || '').trim();
  let kind = 'info';
  for (const [emoji, k] of PREFIXES) {
    if (text.startsWith(emoji)) {
      kind = k;
      text = text.slice(emoji.length).trim();
      break;
    }
  }
  // Emojis enmig del text (p. ex. "Omphalotus olearius ☠️") → text net
  text = text.replace(/\s*[☠️⚠️🌱🪨]+\s*/g, ' ').replace(/\s{2,}/g, ' ').trim();
  return { kind, text };
};
