import { gameHTML } from '../game/assets';
export const GET=()=>new Response(gameHTML,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'}});
