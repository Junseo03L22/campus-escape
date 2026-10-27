import { gameJS } from '../../game/assets';
export const GET=()=>new Response(gameJS,{headers:{'Content-Type':'text/javascript; charset=utf-8','Cache-Control':'no-store'}});
