# Campus Escape 도트 아트

2026-10-29 작업본. 게임 코드와 공개 사이트에는 아직 적용하지 않았습니다.

## 유일한 원본

- `sprite_player.py`, `sprite_professor.py`, `sprite_ta.py`의 GRID는 고정 원본입니다. 명시적인 픽셀 수정 요청 없이 변경하지 않습니다.
- 파생 방향과 애니메이션은 별도 조립 코드로 만듭니다. 모든 프레임은 16×16, 투명 배경입니다.
- `sprite_bag.py`는 별도 갈색 가방 아이템입니다.

## 최신 플레이어 결과물

- `player_sheet.png`: 갈색 가방 착용 걷기 64×64. 행 순서는 아래 / 왼쪽 / 오른쪽 / 위, 열은 4프레임.
- `player_states.png`: 숨기 / 적발 32×16.
- `player_sheet.json`: 프레임 크기, 0부터 시작하는 행·열, 좌표, 8fps 재생 정보.
- `_8x.png`: nearest-neighbor 확대본. GIF는 방향별 미리보기입니다.
- `player_no_bag_sheet.png`, `player_with_bag_sheet.png`: 가방 상태를 분리했던 이전 스냅샷(64×80, 행 순서 아래/위/왼쪽/오른쪽/상태). 최종 방향 수정 전 버전이므로 최신 시트로 혼동하지 않습니다.

교수는 `professor_canonical.png`의 회색 머리·눈썹·팔자주름 정면만 최신 확정본입니다. 교수의 이전 시트는 폐기했으며, 최신 교수 애니메이션은 아직 만들지 않았습니다. 조교 시트는 이전 작업본입니다.

## 코드 조립

Pillow가 필요합니다 (`python -m pip install Pillow`). 같은 폴더에서 다음 순서로 실행합니다.

```sh
python assemble_player_limbs.py
python assemble_player_rpg_walk.py
python assemble_player_up_walk.py
python assemble_player_left_walk.py
python mirror_player_right.py
python pack_player_sheets.py
```

중간 스크립트의 `player_sheet.png`는 임시 배치이므로 마지막 pack 단계까지 실행합니다. 오른쪽은 왼쪽의 각 프레임을 좌우 반전하며 머리 모양을 별도로 생성하지 않습니다. 스크립트는 고정 원본을 수정하지 않습니다.
