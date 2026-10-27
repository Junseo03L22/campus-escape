import{readFileSync,writeFileSync,mkdirSync}from'node:fs';
const js=readFileSync('game/game.js','utf8');if(/<\/script/i.test(js))throw Error('Unexpected closing script tag');
const html=readFileSync('game/index.html','utf8').replace(/@import url\('https:\/\/fonts\.googleapis\.com\/[^\n]*\n/,'').replace(/<script src="game\.js(?:\?[^"]*)?"><\/script>/,()=>'<script>\n'+js+'\n</script>').replaceAll("'Noto Sans KR',sans-serif","'Apple SD Gothic Neo','Malgun Gothic',sans-serif");
mkdirSync('standalone',{recursive:true});writeFileSync('standalone/index.html',html);console.log('Created standalone/index.html (offline normal mode)');
