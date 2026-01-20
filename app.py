from flask import Flask, send_file, make_response
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

# ================= 設定區 =================
TARGET_DATE = datetime(2026, 1, 21, 13, 59, 59)
TEXT_COLOR = (255, 255, 255)       # 文字顏色
FALLBACK_BG_COLOR = (128, 0, 0)    # 萬一讀不到圖片時的備用底色 (酒紅)

# 檔案名稱設定
FONT_FILENAME = "arial.ttf"        # 字體檔 (請確保有上傳)
BG_IMAGE_FILENAME = "bg.jpg"       # 背景圖檔 (請確保有上傳)

# 圖片尺寸 (建議與您的 bg.jpg 尺寸一致)
W, H = 1920, 1920

def draw_text_on_frame(base_image, current_time):
    # 複製一份底圖，以免修改到原始物件
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    # 計算時間差
    diff = TARGET_DATE - current_time
    total_seconds = int(diff.total_seconds())

    if total_seconds < 0:
        time_str = "00時 00分 00秒"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02}時 {minutes:02}分 {seconds:02}秒"

    # 載入字體
    try:
        font_path = os.path.join(os.path.dirname(__file__), FONT_FILENAME)
        font = ImageFont.truetype(font_path, 40)
        label_font = ImageFont.truetype(font_path, 20)
    except:
        font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    # ==========================================
    # 這裡調整文字位置 (X, Y)
    # 若您的背景圖有特定的留白處，請修改這裡的座標
    # ==========================================
    
    # 標題 (例如：最後收單)
    draw.text((20, 35), "最後收單", font=label_font, fill=(255, 230, 230))
    
    # 倒數數字
    draw.text((130, 25), time_str, font=font, fill=TEXT_COLOR)

    return img

@app.route('/countdown.gif')
def countdown_gif():
    frames = []
    now = datetime.now()
    
    # --- [關鍵修改] 預先載入背景圖 ---
    # 這樣做可以大幅減少硬碟讀取次數，提升 Render 效能
    bg_path = os.path.join(os.path.dirname(__file__), BG_IMAGE_FILENAME)
    
    try:
        # 開啟圖片並強制轉為 RGB 模式 (避免 PNG 透明度造成 GIF 破圖)
        base_bg = Image.open(bg_path).convert("RGB")
        # 強制縮放到指定尺寸，避免圖片太大撐爆 GIF
        base_bg = base_bg.resize((W, H))
    except IOError:
        # 如果找不到圖片，就建立純色背景
        print("⚠️ 警告：找不到 bg.jpg，使用純色背景。")
        base_bg = Image.new('RGB', (W, H), color=FALLBACK_BG_COLOR)

    # 生成 10 秒動畫 (10 幀)
    for i in range(10):
        frame_time = now + timedelta(seconds=i)
        # 傳入已經載入好的底圖物件
        img = draw_text_on_frame(base_bg, frame_time)
        frames.append(img)

    # 輸出 GIF
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
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)