from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
left=Image.open(P/'player_left_walk.png').convert('RGBA')
right=Image.new('RGBA',(64,16))
for i in range(4): right.paste(left.crop((16*i,0,16*i+16,16)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(16*i,0))
right.save(P/'player_right_walk.png')
right.resize((512,128),Image.Resampling.NEAREST).save(P/'player_right_walk_8x.png')
with Image.open(P/'player_left_walk_8x.gif') as source:
    frames=[]; durations=[]
    for i in range(source.n_frames):
        source.seek(i); frames.append(source.copy().transpose(Image.Transpose.FLIP_LEFT_RIGHT)); durations.append(source.info.get('duration',125))
    frames[0].save(P/'player_right_walk_8x.gif',save_all=True,append_images=frames[1:],duration=durations,transparency=0,disposal=2,loop=0,optimize=False)
