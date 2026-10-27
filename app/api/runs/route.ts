import { env } from 'cloudflare:workers';
import { handleRankings } from '../../../server/rankings';
export const dynamic='force-dynamic';
export const GET=(request:Request)=>handleRankings(request,env.DB);
export const POST=(request:Request)=>handleRankings(request,env.DB);
