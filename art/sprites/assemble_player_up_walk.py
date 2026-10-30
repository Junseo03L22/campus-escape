"""Rear walk derived by code assembly; frozen canonical sources are read-only."""
from pathlib import Path
import ast, json, hashlib
from PIL import Image
P=Path(__file__).resolve().parent
sources={n:(P/n).read_bytes() for n in ['sprite_player.py','sprite_professor.py','sprite_ta.py']}
tree=ast.parse(sources['sprite_player.py'].decode())
d={t.id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name)}
colors=[tuple(bytes.fromhex(c[1:]))+(255,) for c in d['PALETTE']]
# First three rows retain the canonical hair. Replace facial region with
# rear hair, skin-colored ears (row6), and neck under hair (row8).
REAR_UPPER=tuple(d['GRID'][:3])+(
 '...012111110....',
 '...011111110....',
 '...031111130....',
 '....0111110.....',
 '...007444700....',
 '..0D07DCD70D0...',
 '..0C07DDD70C0...',
 '..0307DCD7030...',
 '...008888800....',
 '....0AAAAA0.....',
)
assert len(REAR_UPPER)==13 and all(len(r)==16 for r in REAR_UPPER)
# Same arm/leg timing as the approved front walk. Only facing changes.
limb_frames=json.loads((P/'player_down_frames.json').read_text())['frames']
frames=[]
parts=[]
for i in range(4):
 rows=list(REAR_UPPER)+list(limb_frames[i][13:])
 # Reuse the exact hand/sleeve pixels from front limb assembly, retaining
 # the new backpack/straps across center columns 5..9.
 for y in range(8,13):
  r=list(rows[y])
  for x in range(16):
   if x<=4 or x>=10: r[x]=limb_frames[i][y][x]
  rows[y]=''.join(r)
 parts.append({'upper':rows[:13], 'lower':rows[13:]})
 if i in (1,3):
  assert rows[0]=='.'*16
  rows[:13]=rows[1:13]+['....0AAAAA0.....']
 frames.append(rows)
assert frames[0]==frames[2]

def render(rows):
 assert len(rows)==16 and all(len(r)==16 for r in rows)
 im=Image.new('RGBA',(16,16))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):
   if c!='.': im.putpixel((x,y),colors[int(c,18)])
 return im
images=[render(f) for f in frames]
strip=Image.new('RGBA',(64,16))
for i,im in enumerate(images): strip.paste(im,(16*i,0))
strip.save(P/'player_up_walk.png')
strip.resize((512,128),Image.Resampling.NEAREST).save(P/'player_up_walk_8x.png')
# Preserve exact colors and transparency in an indexed GIF.
palette=[0,0,0]+[v for c in colors for v in c[:3]]; palette += [0]*(768-len(palette))
lookup={c:i+1 for i,c in enumerate(colors)}; gif=[]
for im in images:
 g=Image.new('P',(16,16)); g.putpalette(palette)
 g.putdata([lookup[p] if p[3] else 0 for p in im.get_flattened_data()])
 gif.append(g.resize((128,128),Image.Resampling.NEAREST))
gif[0].save(P/'player_up_walk_8x.gif',save_all=True,append_images=gif[1:],duration=[120,130,120,130],transparency=0,disposal=2,loop=0,optimize=False)
(P/'player_up_walk_parts.json').write_text(json.dumps({'rear_upper':REAR_UPPER,'pieces_by_frame':parts,'assembled_frames':frames,'fps':8},indent=2))
for name,contents in sources.items(): assert (P/name).read_bytes()==contents
assert all(im.getbbox()[0]==2 and im.getbbox()[2]==13 for im in images)
print('Rear walk generated with immutable source grids, identical limb timing, 1px bob and original 16-color subset.')
