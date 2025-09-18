from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, font, messagebox
import requests
import json
import os

# ======= Cấu hình API Deepseek =======
API_KEY = "YOUR-API-KEY"  # Thay bằng key thật của bạn
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat"

# ======= Các hàm chức năng từ main6.py =======
def get_lyrics_from_deepseek(data):
    """
    Gửi dữ liệu bài hát tới Deepseek API và nhận lại gợi ý lời bài hát
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý tạo lời bài hát."},
            {"role": "user", "content": f"Tạo lời bài hát với dữ liệu: {json.dumps(data, ensure_ascii=False)}"}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Lỗi khi gọi API: {e}"

# ======= Placeholder cho Entry =======
def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg='grey')

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(fg='black')

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# ======= Placeholder cho Text =======
def add_text_placeholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg='grey')

    def on_focus_in(event):
        if text_widget.get("1.0", 'end').strip() == placeholder:
            text_widget.delete("1.0", 'end')
            text_widget.config(fg='black')

    def on_focus_out(event):
        if text_widget.get("1.0", 'end').strip() == "":
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg='grey')

    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)

# ======= Các hàm xử lý sự kiện =======
def reset_fields():
    """Đặt lại tất cả các trường nhập liệu về trạng thái ban đầu."""
    # Reset các Entry
    for entry, ph in zip(entries, entry_placeholders):
        entry.delete(0, 'end')
        add_placeholder(entry, ph)
    
    # Reset các Text
    content_entry.delete("1.0", 'end')
    add_text_placeholder(content_entry, content_placeholder)
    
    target_entry.delete("1.0", 'end')
    add_text_placeholder(target_entry, target_placeholder)

def save_data():
    """
    Lấy dữ liệu từ các trường nhập liệu, kiểm tra tính hợp lệ,
    gọi API để tạo lời bài hát và lưu nội dung vào file .txt.
    """
    # Lấy dữ liệu từ các trường nhập liệu và dọn dẹp khoảng trắng
    data = {
        "title": name_song_entry.get().strip(),
        "listener": TA_entry.get().strip(),
        "goal": target_entry.get("1.0", 'end').strip(),
        "style": style_entry.get().strip(),
        "reference_song": example_entry.get().strip(),
        "content": content_entry.get("1.0", 'end').strip()
    }

    # Danh sách các trường bắt buộc và tên hiển thị tương ứng
    required_fields = [
        ("title", "Tên bài hát", entry_placeholders[0]),
        ("listener", "Người nghe", entry_placeholders[1]),
        ("goal", "Mục tiêu", target_placeholder),
        ("style", "Phong cách", entry_placeholders[3]),
        ("content", "Nội dung", content_placeholder)
    ]

    # Kiểm tra từng trường bắt buộc
    for field_name, display_name, placeholder_text in required_fields:
        if not data[field_name] or data[field_name] == placeholder_text:
            messagebox.showwarning("Thiếu dữ liệu", f"Vui lòng nhập '{display_name}' để tạo lời bài hát.")
            return

    # Nếu tất cả các trường bắt buộc đã được nhập đầy đủ, tiếp tục xử lý
    lyrics = get_lyrics_from_deepseek(data)

    # Lấy tên bài hát để làm tên file
    song_title = data.get("title", "loi_bai_hat_moi")
    file_name = f"{song_title.replace(' ', '_').replace('/', '_')}.txt"

    # Tạo thư mục 'lyrics' nếu chưa tồn tại
    save_dir = "out_put"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_path = os.path.join(save_dir, file_name)

    # Lưu lời bài hát vào file .txt
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"Tên bài hát: {data['title']}\n")
            file.write(f"Người nghe: {data['listener']}\n")
            file.write(f"Mục tiêu: {data['goal']}\n")
            file.write(f"Phong cách: {data['style']}\n")
            file.write(f"Bài tham chiếu: {data['reference_song']}\n")
            file.write(f"Nội dung: {data['content']}\n\n")
            file.write("--- Lời bài hát ---\n")
            file.write(lyrics)

        messagebox.showinfo("Lưu thành công", f"Lời bài hát đã được lưu vào file:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

# ======= Giao diện từ main.py =======
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\Leetcoode\Giaiphap\assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.geometry("1440x1024")
window.configure(bg = "#FFFFFF")

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 1024,
    width = 1440,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    720.0,
    512.0,
    image=image_image_1
)

# Tạo font mới
entry_font = font.Font(family="Crimson Pro SemiBold", size=20)

# Tạo các widget và đặt placeholder
content_entry_image = PhotoImage(
    file=relative_to_assets("content_entry.png"))
content_entry_bg = canvas.create_image(
    724.5,
    365.5,
    image=content_entry_image
)
content_entry = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    wrap="word",
    padx=0,
    pady=0
)
content_entry.place(
    x=80.0,
    y=316.0,
    width=1289.0,
    height=97.0
)
content_placeholder = "Nhập nội dung bạn muốn truyền tải"
add_text_placeholder(content_entry, content_placeholder)

target_entry_image = PhotoImage(
    file=relative_to_assets("target_entry.png"))
target_entry_bg = canvas.create_image(
    724.5,
    569.5,
    image=target_entry_image
)
target_entry = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    wrap="word",
    padx=0,
    pady=0
)
target_entry.place(
    x=80.0,
    y=520.0,
    width=1289.0,
    height=97.0
)
target_placeholder = "Nhập mục tiêu của bài hát"
add_text_placeholder(target_entry, target_placeholder)

TA_entry_image = PhotoImage(
    file=relative_to_assets("TA_entry.png"))
TA_entry_bg = canvas.create_image(
    882.0,
    195.0,
    image= TA_entry_image
)
TA_entry = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    justify="left"
)
TA_entry.place(
    x=393.0,
    y=176.0,
    width=978.0,
    height=36.0
)

name_song_entry_image = PhotoImage(
    file=relative_to_assets("name_song_entry.png"))
name_song_entry_bg = canvas.create_image(
    882.0,
    104.0,
    image=name_song_entry_image
)
name_song_entry= Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    justify="left"
)
name_song_entry.place(
    x=274.0,
    y=85.0,
    width=1097.0,
    height=36.0
)

style_entry_image = PhotoImage(
    file=relative_to_assets("style_entry.png"))
style_entry_bg = canvas.create_image(
    882.0,
    697.0,
    image=style_entry_image
)
style_entry = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    justify="left"
)
style_entry.place(
    x=393.0,
    y=678.0,
    width=978.0,
    height=36.0
)

example_entry_image = PhotoImage(
    file=relative_to_assets("example_entry.png"))
example_entry_bg = canvas.create_image(
    882.0,
    788.0,
    image=example_entry_image
)
example_entry = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=entry_font,
    justify="left"
)
example_entry.place(
    x=393.0,
    y=769.0,
    width=978.0,
    height=36.0
)

# Tạo danh sách các entry để quản lý
entry_placeholders = [
    "Nhập tên bài hát",
    "Nhập người nghe",
    "Nhập phong cách",
    "Nhập bài tham chiếu"
]

entries = [name_song_entry, TA_entry, style_entry, example_entry]

# Thêm placeholder cho các entry
for entry, placeholder in zip(entries, entry_placeholders):
    add_placeholder(entry, placeholder)

# Nút reset và save
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=reset_fields,
    relief="flat"
)
button_1.place(
    x=178.0,
    y=922.0,
    width=405.0,
    height=76.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=save_data,
    relief="flat"
)
button_2.place(
    x=636.0,
    y=922.0,
    width=735.0,
    height=76.0
)

window.resizable(False, False)
window.mainloop()