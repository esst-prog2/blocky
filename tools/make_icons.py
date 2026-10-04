"""Draw Blocky's icon in each theme's colours and write every size the app, browser and extension use.

Run from the repository root: python tools/make_icons.py
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blocky.theme import THEMES  # noqa: E402

FONT = r"C:\Windows\Fonts\segoeuib.ttf"
ICON_SIZES = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]


def colours(theme: str) -> tuple[str, str]:
    """Square and letter colour. Forest keeps its deep square; the others use their button colour so the icon
    stands out at 16 pixels."""
    roles = THEMES[theme]
    if theme == "forest":
        return roles["DEEP"], roles["ACCENT"]
    return roles["PRIMARY"], roles["ON_PRIMARY"]


def draw(square: str, letter: str, size: int = 512) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas = ImageDraw.Draw(image)
    margin = size // 32
    canvas.rounded_rectangle((margin, margin, size - margin, size - margin), radius=size * 7 // 32, fill=square)
    font = ImageFont.truetype(FONT, size * 2 // 3)
    left, top, right, bottom = canvas.textbbox((0, 0), "B", font=font)
    x = (size - (right - left)) / 2 - left
    y = (size - (bottom - top)) / 2 - top
    canvas.text((x, y), "B", font=font, fill=letter)
    return image


def main() -> None:
    for theme in THEMES:
        draw(*colours(theme)).save(ROOT / f"blocky/assets/blocky-{theme}.ico", sizes=ICON_SIZES)
    # The Start-menu shortcut and the extension keep the Forest icon.
    forest = draw(*colours("forest"))
    forest.save(ROOT / "blocky/assets/blocky.ico", sizes=ICON_SIZES)
    for size in (16, 32, 48, 128):
        forest.resize((size, size), Image.LANCZOS).save(ROOT / f"extension/icons/icon-{size}.png")
    print("icons written")


if __name__ == "__main__":
    main()
