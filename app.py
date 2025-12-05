from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
import os, uuid

app = Flask(__name__)
OUTPUT_DIR = "static/generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_text_on_image(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    try:
        font_size = max(20, w // 15)
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    def draw_centered(text, y):
        text = text.upper()
        current_font = font
        bbox = draw.textbbox((0, 0), text, font=current_font)
        tw = bbox[2] - bbox[0]

        while tw > w - 20 and current_font.size > 10:
            new_size = max(10, current_font.size - 1)
            try:
                current_font = ImageFont.truetype("arial.ttf", new_size)
            except Exception:
                current_font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=current_font)
            tw = bbox[2] - bbox[0]

        x = (w - tw) / 2
        th = bbox[3] - bbox[1]
        outline_range = max(1, int(current_font.size / 15)) if hasattr(current_font, "size") else 1
        for ox in range(-outline_range, outline_range+1):
            for oy in range(-outline_range, outline_range+1):
                draw.text((x+ox, y+oy), text, font=current_font, fill="black")
        draw.text((x, y), text, font=current_font, fill="white")

    if top_text:
        draw_centered(top_text, 10)
    if bottom_text:
        draw_centered(bottom_text, h - 10 - font.size)

    return img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded = request.files.get("image")
        top = request.form.get("top_text", "")
        bottom = request.form.get("bottom_text", "")

        if not uploaded:
            return render_template("index.html", error="No file uploaded.")

        img = Image.open(uploaded).convert("RGB")
        img = draw_text_on_image(img, top, bottom)

        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, format="PNG")

        return render_template("index.html", meme_path=path)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
