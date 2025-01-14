import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
from tkinter import messagebox  # Thêm để hiển thị thông báo
import numpy as np
import cv2


def import_image():
    # Chọn file ảnh
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if file_path:
        try:
            # Mở và hiển thị ảnh gốc
            global img  # Để có thể truy cập ảnh toàn cục
            img = Image.open(file_path)
            img.thumbnail((480, 320))  # Giới hạn kích thước ảnh gốc
            img_tk = ImageTk.PhotoImage(img)

            original_image_label.config(image=img_tk)
            original_image_label.image = img_tk

            # Reset ảnh chỉnh sửa về trống (chưa làm chỉnh sửa gì)
            edited_image_label.config(image="", text="Chưa chỉnh sửa")
            edited_image_label.image = None
        except Exception as e:
            print(f"Error: {e}")


def save_image():
    global edited_img
    if edited_img is None:
        messagebox.showwarning("Cảnh báo", "Chưa chỉnh sửa ảnh!")
        return

    # Tạo cửa sổ tùy chọn
    save_window = tk.Toplevel(root)
    save_window.title("Lưu Ảnh")
    save_window.geometry("400x200")
    save_window.resizable(False, False)

    def save_as_new():
        # Lưu ảnh đã chỉnh sửa thành ảnh mới
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("BMP files", "*.bmp")],
        )
        if save_path:
            try:
                edited_img.save(save_path)
                messagebox.showinfo("Thông báo", "Đã lưu ảnh mới thành công!")
                save_window.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu ảnh: {e}")

    def replace_original():
        global img, edited_img
        if edited_img is None:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh chỉnh sửa để thay thế!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thay thế ảnh gốc?"):
            try:
                # Ghi đè ảnh chỉnh sửa lên ảnh gốc
                img_path = img.filename  # Đường dẫn ảnh gốc
                edited_img.save(img_path)  # Lưu ảnh chỉnh sửa đè lên ảnh gốc
                img = edited_img.copy()  # Cập nhật ảnh gốc trong chương trình
                messagebox.showinfo("Lưu ảnh thành công!", "Ảnh gốc đã được thay thế!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thay thế ảnh gốc: {e}")

    def close_window():
        save_window.destroy()

    # Thêm các nút lựa chọn
    tk.Label(save_window, text="Chọn phương thức lưu ảnh:", font=("Arial", 12)).pack(pady=10)

    tk.Button(save_window, text="Lưu thành ảnh mới", command=save_as_new, width=30).pack(pady=5)
    tk.Button(save_window, text="Thay thế ảnh gốc", command=replace_original, width=30).pack(pady=5)
    tk.Button(save_window, text="Thoát", command=close_window, width=30).pack(pady=5)


def apply_filter(filter_type):
    # Áp dụng bộ lọc vào ảnh gốc
    global img, edited_img
    if img:
        if filter_type == "BLUR":
            edited_img = img.filter(ImageFilter.BLUR)
        elif filter_type == "CONTOUR":
            edited_img = img.filter(ImageFilter.CONTOUR)
        elif filter_type == "DETAIL":
            edited_img = img.filter(ImageFilter.DETAIL)
        elif filter_type == "SHARPEN":
            edited_img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == "SMOOTH":
            edited_img = img.filter(ImageFilter.SMOOTH)

        # Hiển thị ảnh đã chỉnh sửa
        edited_img_tk = ImageTk.PhotoImage(edited_img)
        edited_image_label.config(image=edited_img_tk, text="")
        edited_image_label.image = edited_img_tk


# Threshold Segmentation
def apply_threshold():
    global img, edited_img
    if img:
        grayscale = img.convert("L")  # Chuyển ảnh về dạng đen trắng (grayscale)
        threshold_value = 128  # Ngưỡng mặc định, có thể thay đổi
        thresholded = grayscale.point(lambda p: p > threshold_value and 255)

        edited_img = thresholded
        edited_img_tk = ImageTk.PhotoImage(edited_img)
        edited_image_label.config(image=edited_img_tk, text="")
        edited_image_label.image = edited_img_tk


# K-Means Clustering
def apply_kmeans():
    global img, edited_img
    if img:
        # Chuyển ảnh về dạng numpy array
        img_np = np.array(img)

        # Chuyển ảnh sang định dạng 2D (pixel, 3 màu)
        Z = img_np.reshape((-1, 3))
        Z = np.float32(Z)

        # Thực hiện K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 4  # Số lượng cụm (clusters)
        _, labels, centers = cv2.kmeans(Z, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Chuyển đổi lại cụm trung tâm về giá trị pixel
        centers = np.uint8(centers)
        segmented_image = centers[labels.flatten()]
        segmented_image = segmented_image.reshape(img_np.shape)

        edited_img = Image.fromarray(segmented_image)
        edited_img_tk = ImageTk.PhotoImage(edited_img)
        edited_image_label.config(image=edited_img_tk, text="")
        edited_image_label.image = edited_img_tk


def exit_app():
    root.quit()


# -------------------------------TẠO GIAO DIỆN---------------------------------#
# Tạo giao diện chính
root = tk.Tk()
root.title("TTTN-ImageProcessingApp")
root.geometry("960x540")

# Tạo menu bar
menu_bar = tk.Menu(root)

options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Chọn Ảnh", command=import_image)  # Thêm tùy chọn "Import Ảnh"
options_menu.add_separator()  # Dòng ngăn cách

# Tạo menu con cho bộ lọc
filter_menu = tk.Menu(options_menu, tearoff=0)
filter_menu.add_command(label="Làm mờ", command=lambda: apply_filter("BLUR"))
filter_menu.add_command(label="Contour", command=lambda: apply_filter("CONTOUR"))
filter_menu.add_command(label="Chi tiết", command=lambda: apply_filter("DETAIL"))
filter_menu.add_command(label="Làm nét", command=lambda: apply_filter("SHARPEN"))
filter_menu.add_command(label="Làm mượt", command=lambda: apply_filter("SMOOTH"))

# Thêm hai chức năng vào menu
filter_menu.add_command(label="Threshold Segmentation", command=apply_threshold)
filter_menu.add_command(label="K-Means Clustering", command=apply_kmeans)

options_menu.add_cascade(label="Chọn Bộ Lọc", menu=filter_menu)  # Thêm menu con vào Options
options_menu.add_separator()
options_menu.add_command(label="Lưu Ảnh", command=save_image)  # Thêm vào menu "Options"
options_menu.add_separator()
options_menu.add_command(label="Thoát", command=exit_app)  # Thêm tùy chọn "Thoát"

menu_bar.add_cascade(label="Options", menu=options_menu)  # Thêm menu "Options" vào menu bar

root.config(menu=menu_bar)

# Chia giao diện thành hai phần
main_frame = tk.Frame(root, bg="lightgray", width=960, height=540)
main_frame.pack(fill="both", expand=True)

# Khung bên trái (ảnh gốc)
left_panel = tk.Frame(main_frame, width=480, height=540, bg="lightblue")
left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

original_label = tk.Label(left_panel, text="Ảnh Gốc", bg="lightblue", font=("Arial", 14))
original_label.pack(pady=10)

original_image_label = tk.Label(left_panel, bg="white", width=480, height=320, text="Chọn ảnh để chỉnh sửa!",
                                font=("Arial", 24))
original_image_label.pack(pady=20)

# Khung bên phải (ảnh chỉnh sửa)
right_panel = tk.Frame(main_frame, width=480, height=540, bg="lightgreen")
right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

edited_label = tk.Label(right_panel, text="Ảnh Đã Chỉnh Sửa", bg="lightgreen", font=("Arial", 14))
edited_label.pack(pady=10)

edited_image_label = tk.Label(right_panel, bg="white", width=480, height=320, text="Chưa có chỉnh sửa")
edited_image_label.pack(pady=20)

# Chạy giao diện
root.mainloop()
