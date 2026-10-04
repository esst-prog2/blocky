"""Draw Blocky's icon once and write every size the app, browser and extension use.

Run from the repository root: python tools/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DEEP = "#2B5748"
SAGE = "#9CB080"
FONT = r"C:\Windows\Fonts\segoeuib.ttf"


def draw(size: int = 512) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas = ImageDraw.Draw(image)
    margin = size // 32
    canvas.rounded_rectangle((margin, margin, size - margin, size - margin), radius=size * 7 // 32, fill=DEEP)
    font = ImageFont.truetype(FONT, size * 2 // 3)
    left, top, right, bottom = canvas.textbbox((0, 0), "B", font=font)
    x = (size - (right - left)) / 2 - left
    y = (size - (bottom - top)) / 2 - top
    canvas.text((x, y), "B", font=font, fill=SAGE)
    return image


def main() -> None:
    icon = draw()
    icon.save(ROOT / "blocky/assets/blocky.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    for size in (16, 32, 48, 128):
        icon.resize((size, size), Image.LANCZOS).save(ROOT / f"extension/icons/icon-{size}.png")
    print("icons written")


if __name__ == "__main__":
    main()
