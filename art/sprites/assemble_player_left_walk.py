"""Left profile, independent limb assembly, original palette and frozen sources."""
from pathlib import Path
import ast,json
from PIL import Image
P=Path(__file__).resolve().parent
sources={n:(P/n).read_bytes() for n in ['sprite_player.py','sprite_professor.py','sprite_ta.py']}
d={t.id:ast.literal_eval(n.value) for n in ast.parse(sources['sprite_player.py'].decode()).body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name)}
colors=[tuple(bytes.fromhex(c[1:]))+(255,) for c in d['PALETTE']]
# Explicit profile upper-body grid; x=3 small nose, x=4 one visible eye.
# The rear backpack uses only the approved original brown colors 1 and 2.
UPPER=(
 '................',
 '.....00000......',
 '....0122210.....',
 '...012111110....',
 '....04541110....',
 '....04041110....',
 '....06441110....',
 '.....034400.....',
 '....0944880120..',
 '....0888870220..',
 '....0788870210..',
 '....0088800110..',
)
assert len(UPPER)==12 and all(len(r)==16 for r in UPPER)
# Lower rows 13..16: wide contact poses and narrow passing poses.
LOWER=(
 ('....0BAAAB0.....','...0BA00AAB0....','..0EF0..0FE0....','..0000..0000....'),
 ('.....0BAAB0.....','.....0AAB0......','.....0EF0.......','.....0000.......'),
 ('....0BAAAB0.....','...0AA00BAB0....','..0FE0..0EF0....','..0000..0000....'),
 ('.....0ABAB0.....','......0BA0......','......0FE0......','......0000......'),
)
# Arms occupy only sleeve/hand pixels; head, torso, bag move as rigid pieces.
# Contact: forearm counter-swings horizontally; passing: arm below shoulder.
ARMS=(
 ((5,9,'7'),(5,10,'3'),(6,10,'0')),
 ((6,9,'7'),(6,10,'3'),(6,11,'0')),
 ((7,9,'7'),(8,10,'3'),(8,11,'0')),
 ((6,9,'7'),(7,10,'3'),(7,11,'0')),
)
frames=[]; images=[]
for i in range(4):
 dy=1 if i in (0,2) else -1
 upper=[list(r) for r in UPPER]
 for x,y,c in ARMS[i]: upper[y][x]=c
 grid=[list('.'*16) for _ in range(16)]
 for y,row in enumerate(upper):
  for x,c in enumerate(row):
   if c!='.':
    assert 0<=y+dy<16
    grid[y+dy][x]=c
 # Join waist to trousers without rescaling the torso.
 for y,row in enumerate(LOWER[i],12):
  for x,c in enumerate(row):
   if c!='.': grid[y][x]=c
 if dy==-1:
  for x,c in enumerate('....00AAA00.....'):
   if c!='.': grid[11][x]=c
 rows=[''.join(r) for r in grid]; frames.append(rows)
 im=Image.new('RGBA',(16,16))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):
   if c!='.': im.putpixel((x,y),colors[int(c,18)])
 images.append(im)
strip=Image.new('RGBA',(64,16))
for i,im in enumerate(images): strip.paste(im,(i*16,0))
strip.save(P/'player_left_walk.png')
strip.resize((512,128),Image.Resampling.NEAREST).save(P/'player_left_walk_8x.png')
pal=[0,0,0]+[v for c in colors for v in c[:3]];pal += [0]*(768-len(pal))
lookup={c:i+1 for i,c in enumerate(colors)};gif=[]
for im in images:
 g=Image.new('P',(16,16));g.putpalette(pal);g.putdata([lookup[p] if p[3] else 0 for p in im.get_flattened_data()]);gif.append(g.resize((128,128),Image.Resampling.NEAREST))
gif[0].save(P/'player_left_walk_8x.gif',save_all=True,append_images=gif[1:],duration=[120,130,120,130],loop=0,transparency=0,disposal=2,optimize=False)
(P/'player_left_walk_parts.json').write_text(json.dumps({'upper':UPPER,'lower_poses':LOWER,'arms':ARMS,'frames':frames,'fps':8},indent=2))
for name,data in sources.items(): assert (P/name).read_bytes()==data
print('Created left walk contact/pass/opposite contact/pass; fixed palette, 16x16 cells, canonical sources unchanged.')
