#!/usr/bin/env python3
"""Git Animals 농장 SVG에서 왼쪽 위 사용자 이름 블록만 제거한다.

사용법: strip_farm_name.py <입력.svg> <출력.svg>

농장 SVG에는 <g id="username"> 요소가 여러 개 있다. 동물마다 붙는 것은
display:none 으로 숨겨져 있고, 화면에 보이는 것은 배경이 그리는 하나뿐이다.
보이는 블록이 정확히 하나가 아니면 형식이 바뀐 것으로 보고 실패시켜,
이름이 남은 이미지가 올라가지 않게 한다.
"""
import re
import sys
import xml.etree.ElementTree as ET

USERNAME_OPEN = re.compile(r'<g id="username"[^>]*>')
G_TAG = re.compile(r"<g\b[^>]*>|</g>")


def element_end(svg: str, open_match: re.Match) -> int:
    """open_match 로 시작한 <g> 요소가 끝나는 위치(닫는 태그 뒤)를 돌려준다."""
    if open_match.group().endswith("/>"):
        return open_match.end()
    depth = 1
    for tag in G_TAG.finditer(svg, open_match.end()):
        text = tag.group()
        if text == "</g>":
            depth -= 1
            if depth == 0:
                return tag.end()
        elif not text.endswith("/>"):
            depth += 1
    raise ValueError("username 블록의 닫는 태그를 찾지 못했습니다.")


def strip_username(svg: str) -> str:
    visible = [
        m for m in USERNAME_OPEN.finditer(svg) if "display:none" not in m.group()
    ]
    if len(visible) != 1:
        raise ValueError(
            f"보이는 username 블록이 {len(visible)}개입니다(1개여야 함). "
            "Git Animals SVG 형식이 바뀌었을 수 있습니다."
        )
    start = visible[0].start()
    return svg[:start] + svg[element_end(svg, visible[0]):]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        svg = f.read()
    try:
        result = strip_username(svg)
        ET.fromstring(result)  # 잘라낸 뒤에도 올바른 XML인지 확인
    except (ValueError, ET.ParseError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(result)
    print(f"이름 블록 제거 완료: {len(svg)} -> {len(result)}자")
    return 0


if __name__ == "__main__":
    sys.exit(main())
