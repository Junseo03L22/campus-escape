"""Immutable body + independent arm/leg pieces. No source-grid writes."""
from pathlib import Path
import ast, hashlib, json
from PIL import Image
P=Path(__file__).resolve().parent
src=P/'sprite_player.py'; original_bytes=src.read_bytes()
d={t.id:ast.literal_eval(n.value) for n in ast.parse(original_bytes.decode()).body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name)}
G=d['GRID']; colors=[tuple(bytes.fromhex(c[1:]))+(255,) for c in d['PALETTE']]
# Partition masks, using screen-left/screen-right names. Shoulder row 9 fixed.
parts={'left_arm':[], 'right_arm':[], 'left_leg':[], 'right_leg':[], 'body':[]}
for y in range(16):
 for x in range(16):
  name='body'
  if 8<=y<=11 and x<=4: name='left_arm'
  elif 8<=y<=11 and x>=10: name='right_arm'
  elif y==12 and x<=3: name='left_arm'
  elif y==12 and x>=11: name='right_arm'
  elif y>=13 and x<=6: name='left_leg'
  elif y>=13 and x>=7: name='right_leg'
  elif y==12 and 4<=x<=6: name='left_leg'
  elif y==12 and 7<=x<=10: name='right_leg'
  parts[name].append((x,y))
# Save the pieces as full 16x16 character grids, all using original pixels.
piece_grids={name:[''.join(G[y][x] if (x,y) in mask else '.' for x in range(16)) for y in range(16)] for name,mask in parts.items()}
(P/'player_limb_parts.json').write_text(json.dumps({'source':'sprite_player.py','coordinates':'screen-left/right','pieces':piece_grids},indent=2))

def posed(left_front):
 rows=[list(r) for r in G]
 def put(x,y,c): rows[y][x]=c
 # Hand-tip positions only; shoulders and proximal arms stay at original sites.
 # Rear hand up 1px; forward hand down 1px, with same x coordinates.
 for left in (True,False):
  x=3 if left else 11
  forward=(left!=left_front) # opposite arm from stepping foot
  put(x,10,'7')
  if forward:
   put(x,11,'3'); put(x,12,'0')
   put(x-1 if left else x+1,11,'0')
  else: put(x,9,'3')
 # Shoe columns stay original: left 3..6, right 7..10.
 # A forward shoe is down 1px (bottom row); rear shoe up 1px.
 for left in (True,False):
  front=(left==left_front)
  x=3 if left else 7
  if front:
   for dx,c in enumerate('0AA0'): put(x+dx,14,c)
   for dx,c in enumerate('0EF0' if left else '0FE0'): put(x+dx,15,c)
  else:
   for dx,c in enumerate('0EF0' if left else '0FE0'): put(x+dx,13,c)
   for dx,c in enumerate('0000'): put(x+dx,14,c)
   for dx in range(4): put(x+dx,15,'.')
 return [''.join(r) for r in rows]
frames=[list(G),posed(True),list(G),posed(False)]
for frame in frames:
 for x,y in parts['body']: assert frame[y][x]==G[y][x]
 assert frame[:9]==list(G[:9]) # includes shoulders
assert frames[0]==frames[2]==list(G)

def render(rows):
 im=Image.new('RGBA',(16,16))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):
   if c!='.': im.putpixel((x,y),colors[int(c,18)])
 return im
images=[render(g) for g in frames]
assert len({im.getbbox() for im in images})==1, [im.getbbox() for im in images]
strip=Image.new('RGBA',(64,16))
for i,im in enumerate(images): strip.paste(im,(i*16,0))
strip.save(P/'player_down_strip.png')
strip.resize((512,128),Image.Resampling.NEAREST).save(P/'player_down_strip_8x.png')
sheet=Image.open(P/'player_with_bag_sheet.png').convert('RGBA'); sheet.paste(strip,(0,0)); sheet.save(P/'player_sheet.png'); sheet.resize((512,640),Image.Resampling.NEAREST).save(P/'player_sheet_8x.png')
pal=[0,0,0]+[v for c in colors for v in c[:3]]; pal += [0]*(768-len(pal)); lookup={c:i+1 for i,c in enumerate(colors)}; gif=[]
for im in images:
 g=Image.new('P',(16,16)); g.putpalette(pal); g.putdata([lookup[p] if p[3] else 0 for p in im.get_flattened_data()]); gif.append(g.resize((128,128),Image.Resampling.NEAREST))
gif[0].save(P/'player_walk_down_8x.gif',save_all=True,append_images=gif[1:],duration=[120,130,120,130],loop=0,transparency=0,disposal=2,optimize=False)
(P/'player_down_frames.json').write_text(json.dumps({'frames':frames},indent=2))
assert src.read_bytes()==original_bytes
print('Verified: source unchanged; body/shoulders fixed; frames 1=3=source; all bounding boxes identical:',images[0].getbbox())
