from flask import Flask, send_file, make_response, redirect
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import os  # <--- 確保這行一定要有！
import traceback # 用來印出詳細錯誤

app = Flask(__name__)

# ================= 設定區 =================
TARGET_DATE = datetime(2026, 1, 21, 13, 59, 59)
BG_COLOR = (128, 0, 0)
TEXT_COLOR = (255, 255, 255)

FONT_FILENAME = "arial.ttf"
BG_IMAGE_FILENAME = "bg.jpg"
W, H = 1920, 1920

def draw_text_on_frame(base_image, current_time):
    # 複製底圖
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    diff = TARGET_DATE - current_time
    total_seconds = int(diff.total_seconds())

    if total_seconds < 0:
        time_str = "00時 00分 00秒"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02}時 {minutes:02}分 {seconds:02}秒"

    # 嘗試載入字體 (加入更詳細的錯誤處理)
    try:
        font_path = os.path.join(os.path.dirname(__file__), FONT_FILENAME)
        font = ImageFont.truetype(font_path, 40)
        label_font = ImageFont.truetype(font_path, 20)
    except Exception as e:
        # 如果字體讀取失敗，印出原因到 Log，並使用預設
        print(f"⚠️ 字體載入失敗 ({e})，使用預設字體")
        font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    draw.text((20, 35), "最後收單", font=label_font, fill=(255, 230, 230))
    draw.text((130, 25), time_str, font=font, fill=TEXT_COLOR)

    return img

@app.route('/')
def index():
    return redirect('/countdown.gif')

@app.route('/countdown.gif')
def countdown_gif():
    try:
        frames = []
        now = datetime.now()
        
        # --- 測試背景圖路徑 ---
        bg_path = os.path.join(os.path.dirname(__file__), BG_IMAGE_FILENAME)
        
        # 嘗試載入背景圖
        try:
            if os.path.exists(bg_path):
                base_bg = Image.open(bg_path).convert("RGB")
                base_bg = base_bg.resize((W, H))
            else:
                print(f"⚠️ 找不到背景圖: {bg_path}，將使用純色背景")
                base_bg = Image.new('RGB', (W, H), color=BG_COLOR)
        except Exception as e:
            print(f"⚠️ 背景圖讀取錯誤: {str(e)}，將使用純色背景")
            base_bg = Image.new('RGB', (W, H), color=BG_COLOR)

        # 生成動畫
        for i in range(10):
            frame_time = now + timedelta(seconds=i)
            img = draw_text_on_frame(base_bg, frame_time)
            frames.append(img)

        output = io.BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=1000,
            loop=0
        )
        output.seek(0)

        response = make_response(send_file(output, mimetype='image/gif'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    except Exception as e:
        # 🚨 關鍵：如果發生任何錯誤，直接印在網頁上給你看 🚨
        error_msg = traceback.format_exc()
        return f"<h1>程式出錯了 (Debug Mode)</h1><pre>{error_msg}</pre>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)