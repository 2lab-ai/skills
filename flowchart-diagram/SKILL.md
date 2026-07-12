# flowchart-diagram — 미니멀 플로우차트 다이어그램

"How to Adult" 책 스타일의 미니멀 결정 플로우차트 렌더러.
흰 배경 + 흑백(#2B2B2B) & 오렌지(#F0511E) + Y/N 다이아몬드 + 직각 화살표 + 상하 오렌지 룰.
(대표님 취향: 바우하우스/미니멀/모노톤+포인트컬러)

**Triggers:** "다이어그램", "플로우차트", "flowchart", "순서도", "결정 트리", "decision tree", "이런 다이어그램 그려줘"

---

## 사용법

```
"이거 플로우차트로 그려줘 [내용]"
"결정 트리 만들어줘: ..."
```

1. 내용을 받으면 → spec(JSON)으로 노드/엣지 좌표 설계
2. flowchart.py 로 SVG 생성 → chromium headless 로 PNG 렌더
3. 텔레그램 send_photo 로 전송

## CLI

```bash
# 내장 예제(Bath or shower?)
python3 ~/2lab.ai/skills/flowchart-diagram/scripts/flowchart.py \
  --example --output ~/2lab.ai/.tmp-render/out.png

# 커스텀 spec
python3 ~/2lab.ai/skills/flowchart-diagram/scripts/flowchart.py \
  --spec myflow.json --output ~/2lab.ai/.tmp-render/out.png
```

## ⚠️ 중요: 출력 경로는 반드시 $HOME 아래로
스냅(snap) chromium이라 `/tmp`에 스크린샷을 못 씀 (조용히 실패).
→ 출력/작업 경로는 `~/2lab.ai/...` 아래로. (스크립트가 내부적으로 `~/2lab.ai/.tmp-render` 사용)
의존성 없음 (Python stdlib + chromium-browser).

## Spec 스키마 (좌표 직접 배치, v1)

```json
{
  "title": "Bath or shower?",
  "width": 860, "height": 1220, "rules": true,
  "boxes": [
    {"id":"q1","x":300,"y":110,"w":260,"h":58,"text":"Do you have a bath?","style":"question"},
    {"id":"a1","x":60,"y":520,"w":220,"h":56,"text":"Have a shower","style":"action","font_size":20}
  ],
  "diamonds": [ {"x":195,"y":250,"label":"N"}, {"x":560,"y":250,"label":"Y"} ],
  "edges": [
    {"points":[[430,168],[430,210],[195,210],[195,234]],"color":"black"},
    {"points":[[195,266],[195,320]],"color":"black","arrow":true}
  ]
}
```

| 요소 | 설명 |
|------|------|
| box.style | `question`(검정 테두리/글자) / `action`(오렌지) / `plain` |
| box.font_size | 글자 크기(기본 22). 긴 텍스트는 20 이하 권장 |
| diamond.label | `Y`(오렌지 채움) / `N`(검정 채움), 흰 글자 |
| diamond.r | 반경(기본 16) |
| edge.points | `[[x,y],...]` 직각 꺾임 폴리라인 |
| edge.color | `black`(#2B2B2B) / `orange`(#F0511E) |
| edge.arrow | 끝에 화살표(기본 true) |
| rules | 상/하단 오렌지 가로줄(기본 true) |

## 스타일 토큰
- 배경 흰색 / DARK `#2B2B2B` / ORANGE `#F0511E`
- 폰트: Helvetica/Arial 계열 sans
- 박스: 흰 채움 + 2px 테두리, rx=2
- 다이아몬드: 회전 사각형(polygon), Y=오렌지 N=검정
- 화살표: 작은 삼각형 marker (색상별)
- force-device-scale-factor=2 (2배 해상도)

## 디자인 팁
- 위→아래 흐름, 분기는 좌(N)/우(Y) 또는 좌우 다이아몬드
- 결과(action) 박스는 오렌지, 질문 박스는 검정
- "예" 경로는 오렌지 엣지, "아니오"는 검정 엣지로 강조하면 원본 느낌

## 파일
```
~/2lab.ai/skills/flowchart-diagram/
├── SKILL.md
├── scripts/flowchart.py
└── examples/bathshower.png
```
