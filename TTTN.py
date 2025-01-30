import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import cv2
import numpy as np

# Các hàm xử lý ảnh
def import_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if file_path:
        try:
            global img, img_cv  # Ảnh gốc 
            img = Image.open(file_path)
            img.thumbnail((480, 320))
            img_tk = ImageTk.PhotoImage(img)

            original_image_label.config(image=img_tk)
            original_image_label.image = img_tk

            # Chuyển đổi ảnh sang định dạng OpenCV
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Reset ảnh chỉnh sửa
            edited_image_label.config(image="", text="Chưa chỉnh sửa")
            edited_image_label.image = None
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải ảnh: {e}")

def save_image():
    global edited_img
    if edited_img is None:
        messagebox.showwarning("Cảnh báo", "Chưa chỉnh sửa ảnh!")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("BMP files", "*.bmp")],
    )
    if save_path:
        try:
            edited_img.save(save_path)
            messagebox.showinfo("Thông báo", "Lưu ảnh thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu ảnh: {e}")

def apply_filter(filter_type):
    global img_cv, edited_img
    if img_cv is None:
        messagebox.showwarning("Cảnh báo", "Chưa có ảnh gốc để xử lý!")
        return

    kernel = np.ones((5, 5), np.uint8)  # Kernel 5x5
    if filter_type == "CLOSE":
        processed = cv2.morphologyEx(img_cv, cv2.MORPH_CLOSE, kernel)
    elif filter_type == "OPEN":
        processed = cv2.morphologyEx(img_cv, cv2.MORPH_OPEN, kernel)
    else:
        messagebox.showerror("Lỗi", "Bộ lọc không hợp lệ!")
        return

    # Chuyển đổi OpenCV -> PIL để hiển thị
    processed_rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
    edited_img = Image.fromarray(processed_rgb)
    edited_img_tk = ImageTk.PhotoImage(edited_img)

    # Hiển thị ảnh chỉnh sửa
    edited_image_label.config(image=edited_img_tk, text="")
    edited_image_label.image = edited_img_tk

def exit_app():
    root.quit()

# -------------------- TẠO GIAO DIỆN --------------------
root = tk.Tk()
root.title("TTTN-ImageProcessingApp")
root.geometry("960x540")

menu_bar = tk.Menu(root)
options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Chọn Ảnh", command=import_image)

filter_menu = tk.Menu(options_menu, tearoff=0)
filter_menu.add_command(label="Phép Đóng Ảnh", command=lambda: apply_filter("CLOSE"))
filter_menu.add_command(label="Phép Mở Ảnh", command=lambda: apply_filter("OPEN"))
options_menu.add_cascade(label="Chọn Bộ Lọc", menu=filter_menu)

options_menu.add_command(label="Lưu Ảnh", command=save_image)
options_menu.add_command(label="Thoát", command=exit_app)

menu_bar.add_cascade(label="Options", menu=options_menu)
root.config(menu=menu_bar)

# Khung giao diện
main_frame = tk.Frame(root, bg="lightgray", width=960, height=540)
main_frame.pack(fill="both", expand=True)

# Khung ảnh gốc
left_panel = tk.Frame(main_frame, width=480, height=540, bg="lightblue")
left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

original_label = tk.Label(left_panel, text="Ảnh Gốc", bg="lightblue", font=("Arial", 14))
original_label.pack(pady=10)

original_image_label = tk.Label(left_panel, bg="white", width=480, height=320, text="Chọn ảnh để chỉnh sửa!",
                                font=("Arial", 24))
original_image_label.pack(pady=20)

# Khung ảnh chỉnh sửa
right_panel = tk.Frame(main_frame, width=480, height=540, bg="lightgreen")
right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

edited_label = tk.Label(right_panel, text="Ảnh Đã Chỉnh Sửa", bg="lightgreen", font=("Arial", 14))
edited_label.pack(pady=10)

edited_image_label = tk.Label(right_panel, bg="white", width=480, height=320, text="Chưa có chỉnh sửa")
edited_image_label.pack(pady=20)

root.mainloop()