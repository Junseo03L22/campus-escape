"""Professor sprite: GRID below is the sole canonical pixel source.

Rows are numbered 1..16, columns 1..16. Edit only explicitly requested
rows/pixels; preserve every other character exactly. Do not regenerate GRID
from other sprites, old scripts, images, mirroring, or procedural edits.
Zones: hair rows 1..5, face 4..8, torso 9..14, feet 15..16.
0..9/A..H are palette indices 0..17; '.' is transparent (not a color).
"""
from pathlib import Path
from PIL import Image

PALETTE = (
    '#252B45', '#593C42', '#95604F', '#D98C70',
    '#FFC69B', '#FFE4BD', '#F4879A', '#278B91',
    '#42C6B0', '#9AE8C2', '#4B568A', '#788AC2',
    '#E9A04C', '#FFD779', '#FFF5DD', '#B6C4CE',
    '#C3C7CD', '#626873',  # G: light grey hair; H: dark grey eyebrows
)

GRID = (
    '....0000000.....',  # 01
    '...0GGGGGGG0....',  # 02
    '...0GGGGGGG0....',  # 03
    '...0HH4444HH0...',  # 04
    '...040444404....',  # 05
    '...044344344....',  # 06
    '...003411430....',  # 07
    '...004444400....',  # 08
    '..0E0AAEEAA0E0..',  # 09
    '..0E0AAEEAA0E0..',  # 10
    '..0E0AAEEAA0E0..',  # 11
    '..00AAAEEAAA00..',  # 12
    '..0AAAAAAAAA0...',  # 13
    '...0AAAA0AAA0...',  # 14
    '..0FFF00AAFF0...',  # 15
    '..0000..00000...',  # 16
)

def main():
    assert len(GRID) == 16 and all(len(row) == 16 for row in GRID)
    assert all(c in '.0123456789ABCDEFGH' for row in GRID for c in row)
    colors = [tuple(bytes.fromhex(c[1:])) + (255,) for c in PALETTE]
    image = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(GRID):
        for x, c in enumerate(row):
            if c != '.':
                image.putpixel((x, y), colors[int(c, 18)])
    out = Path(__file__).resolve().parent
    image.save(out / 'professor_canonical.png')
    image.resize((128, 128), Image.Resampling.NEAREST).save(
        out / 'professor_canonical_8x.png'
    )
    print('\n'.join(GRID))

if __name__ == '__main__':
    main()
