"""Pack latest approved direction frames; never edit canonical source grids."""
from pathlib import Path
import ast,json
from PIL import Image
P=Path(__file__).resolve().parent
frozen={n:(P/n).read_bytes() for n in ['sprite_player.py','sprite_professor.py','sprite_ta.py']}
t=ast.parse(frozen['sprite_player.py'].decode());d={a.id:ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) for a in n.targets if isinstance(a,ast.Name)}
colors=[tuple(bytes.fromhex(c[1:]))+(255,) for c in d['PALETTE']]
def brown(im):
 im=im.convert('RGBA')
 for y in range(im.height):
  for x in range(im.width):
   c=im.getpixel((x,y))
   if c==colors[12]: im.putpixel((x,y),colors[1])
   elif c==colors[13]: im.putpixel((x,y),colors[2])
 return im
# The latest front/back source strips still encode their backpack using
# orange/yellow; apply the approved brown mapping only while packing.
sources=[('down','player_rpg_walk.png'),('left','player_left_walk.png'),('right','player_right_walk.png'),('up','player_up_walk.png')]
sheet=Image.new('RGBA',(64,64)); frames={}
for row,(direction,file) in enumerate(sources):
 strip=brown(Image.open(P/file));assert strip.size==(64,16)
 sheet.paste(strip,(0,row*16))
 for col in range(4):
  frames[f'walk_{direction}_{col+1}']={'sheet':'player_sheet.png','row':row,'column':col,'x':col*16,'y':row*16,'width':16,'height':16}
# Read established special states from the original equipped-state sheet,
# avoiding changes to either pose or their backpack colors.
state_source=Image.open(P/'player_with_bag_sheet.png').convert('RGBA')
states=state_source.crop((0,64,32,80));assert states.size==(32,16)
sheet.save(P/'player_sheet.png');sheet.resize((512,512),Image.Resampling.NEAREST).save(P/'player_sheet_8x.png')
states.save(P/'player_states.png');states.resize((256,128),Image.Resampling.NEAREST).save(P/'player_states_8x.png')
for col,name in enumerate(['hide','caught']): frames[name]={'sheet':'player_states.png','row':0,'column':col,'x':col*16,'y':0,'width':16,'height':16}
metadata={
 'frame_size':{'width':16,'height':16},'coordinate_index_base':0,
 'inventory_state':'brown_bag_equipped','palette':list(d['PALETTE']),
 'sheets':{
  'walk':{'image':'player_sheet.png','width':64,'height':64,'rows':4,'columns':4,'row_order':['down','left','right','up'],'frames_per_direction':4,'fps':8,'loop':True},
  'states':{'image':'player_states.png','width':32,'height':16,'rows':1,'columns':2,'column_order':['hide','caught']}
 },'frames':frames}
(P/'player_sheet.json').write_text(json.dumps(metadata,indent=2))
assert sheet.size==(64,64) and len(frames)==18
assert set(sheet.get_flattened_data())<=set(colors)|{(0,0,0,0)}
for n,b in frozen.items():assert (P/n).read_bytes()==b
print('Packed 16 walk frames (down/left/right/up), 2 states, and metadata. Canonical sources unchanged.')
