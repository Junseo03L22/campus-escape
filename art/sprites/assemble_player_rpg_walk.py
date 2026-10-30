"""One-pixel step bounce derived from limb frames; canonical grid stays fixed."""
from pathlib import Path
import json, hashlib, ast
from PIL import Image
P=Path(__file__).resolve().parent
src=P/'sprite_player.py'; source=src.read_bytes()
d={t.id:ast.literal_eval(n.value) for n in ast.parse(source.decode()).body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name)}
colors=[tuple(bytes.fromhex(c[1:]))+(255,) for c in d['PALETTE']]
frames=json.loads((P/'player_down_frames.json').read_text())['frames']
# During a step the complete head/torso/arm shape translates up by 1px.
# No rescaling, mirrored face, or repainting of the upper body.
for i in (1,3):
 upper=frames[i][:13]
 assert upper[0]=='.'*16
 frames[i][:13]=upper[1:]+['.'*16]
 # Extend the top of the trousers into the vacated hip row; shoes remain.
 frames[i][12]='....0ABAAB0.....'

def render(rows):
 im=Image.new('RGBA',(16,16))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):
   if c!='.': im.putpixel((x,y),colors[int(c,18)])
 return im
images=[render(g) for g in frames]
strip=Image.new('RGBA',(64,16))
for i,im in enumerate(images): strip.paste(im,(16*i,0))
strip.save(P/'player_rpg_walk.png')
strip.resize((512,128),Image.Resampling.NEAREST).save(P/'player_rpg_walk_8x.png')
palette=[0,0,0]+[v for c in colors for v in c[:3]]; palette += [0]*(768-len(palette)); lookup={c:i+1 for i,c in enumerate(colors)}; gif=[]
for im in images:
 g=Image.new('P',(16,16)); g.putpalette(palette)
 g.putdata([lookup[p] if p[3] else 0 for p in im.get_flattened_data()])
 gif.append(g.resize((128,128),Image.Resampling.NEAREST))
gif[0].save(P/'player_rpg_walk_8x.gif',save_all=True,append_images=gif[1:],duration=[120,130,120,130],loop=0,transparency=0,disposal=2,optimize=False)
assert src.read_bytes()==source
assert frames[0]==frames[2]==list(d['GRID'])
(P/'player_rpg_walk_frames.json').write_text(json.dumps({'fps':8,'frames':frames},indent=2))
print('Created separate RPG walking preview; canonical source and existing sheet preserved.')
