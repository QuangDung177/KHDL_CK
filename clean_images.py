import cv2
import os
import shutil
import hashlib
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Định nghĩa các thư mục
dataset_dir = "F:/NAM3/KI2/KHDL/Dataset_CK_KHDL/dataset_merged"
output_dir = "F:/NAM3/KI2/KHDL/Dataset_CK_KHDL/dataset_clean"
classes = ["coriander","lime", "greentea_leaf", "papaya_leaf", "centella","kumquat", "lemongrass",   "lemon","apple_leaf" ]

# Danh sách định dạng ảnh hợp lệ
valid_formats = {'.jpg', '.jpeg', '.png'}

# Ngưỡng làm sạch
MIN_SIZE = (128, 128)
TARGET_SIZE = (640, 640)

def is_valid_image(file_path):
    """Kiểm tra xem file có phải là ảnh hợp lệ không"""
    try:
        # Thử mở ảnh bằng PIL để kiểm tra tính toàn vẹn
        img = Image.open(file_path)
        img.verify()  # Xác minh ảnh
        img.close()

        # Thử đọc ảnh bằng OpenCV
        img_cv = cv2.imread(file_path)
        if img_cv is None:
            return False

        return True
    except Exception as e:
        print(f"Lỗi khi kiểm tra ảnh {file_path}: {str(e)}")
        return False

def resize_image(image_path, target_size=TARGET_SIZE):
    """Resize ảnh về kích thước mục tiêu"""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            ratio = min(target_size[0] / img.size[0], target_size[1] / img.size[1])
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            new_img = Image.new("RGB", target_size, (0, 0, 0))
            offset = ((target_size[0] - new_size[0]) // 2, (target_size[1] - new_size[1]) // 2)
            new_img.paste(img, offset)
            return new_img
    except:
        return None

def get_image_hash(file_path):
    """Tính hash của ảnh để phát hiện trùng lặp"""
    try:
        with open(file_path, 'rb') as f:
            img_data = f.read()
            return hashlib.md5(img_data).hexdigest()
    except Exception as e:
        print(f"Lỗi khi tính hash cho {file_path}: {str(e)}")
        return None

def clean_dataset():
    """Làm sạch dataset: xóa ảnh lỗi, ảnh trùng lặp và kiểm tra định dạng"""
    if os.path.exists(output_dir):
        print(f"Xóa thư mục cũ: {output_dir}")
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)
    for cls in classes:
        os.makedirs(os.path.join(output_dir, cls), exist_ok=True)

    image_hashes = {}  # Lưu hash để kiểm tra trùng lặp
    removed_count = 0
    total_count = 0

    for cls in classes:
        input_class_dir = os.path.join(dataset_dir, cls)
        output_class_dir = os.path.join(output_dir, cls)

        if not os.path.exists(input_class_dir):
            print(f"Thư mục {input_class_dir} không tồn tại!")
            continue

        print(f"Đang xử lý lớp: {cls}")
        for img_name in os.listdir(input_class_dir):
            img_path = os.path.join(input_class_dir, img_name)
            total_count += 1

            # Kiểm tra định dạng file
            file_ext = os.path.splitext(img_name)[1].lower()
            if file_ext not in valid_formats:
                print(f"Xóa file không đúng định dạng: {img_path}")
                removed_count += 1
                continue

            # Kiểm tra kích thước ảnh
            try:
                with Image.open(img_path) as img:
                    if img.size[0] < MIN_SIZE[0] or img.size[1] < MIN_SIZE[1]:
                        print(f"Kích thước ảnh không hợp lệ: {img_path}")
                        removed_count += 1
                        continue
            except:
                print(f"Lỗi khi kiểm tra kích thước: {img_path}")
                removed_count += 1
                continue

            # Kiểm tra ảnh hợp lệ
            if not is_valid_image(img_path):
                print(f"Xóa ảnh lỗi: {img_path}")
                removed_count += 1
                continue

            # Kiểm tra ảnh trùng lặp
            img_hash = get_image_hash(img_path)
            if img_hash is None:
                print(f"Xóa ảnh không thể hash: {img_path}")
                removed_count += 1
                continue

            if img_hash in image_hashes:
                print(f"Xóa ảnh trùng lặp: {img_path} (giống với {image_hashes[img_hash]})")
                removed_count += 1
                continue

            # Resize và sao chép ảnh hợp lệ
            resized_img = resize_image(img_path)
            if resized_img is None:
                print(f"Xóa ảnh không thể resize: {img_path}")
                removed_count += 1
                continue

            dest_path = os.path.join(output_class_dir, img_name)
            base, ext = os.path.splitext(img_name)
            counter = 1
            while os.path.exists(dest_path):
                new_img_name = f"{base}_{counter}{ext}"
                dest_path = os.path.join(output_class_dir, new_img_name)
                counter += 1

            resized_img.save(dest_path)
            image_hashes[img_hash] = dest_path
            print(f"Đã xử lý và sao chép: {dest_path}")

    print(f"\nKết quả làm sạch:")
    print(f"Tổng số file đã kiểm tra: {total_count}")
    print(f"Số file đã xóa: {removed_count}")
    print(f"Số file còn lại: {total_count - removed_count}")

    print("\nSố lượng ảnh trong mỗi lớp sau khi làm sạch:")
    class_counts = {}
    for cls in classes:
        class_path = os.path.join(output_dir, cls)
        if os.path.exists(class_path):
            num_images = len([f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))])
            class_counts[cls] = num_images
            print(f"Lớp {cls}: {num_images} ảnh")

    # Vẽ biểu đồ phân bố số lượng ảnh
    plt.figure(figsize=(10, 6))
    plt.bar(class_counts.keys(), class_counts.values(), color='blue')
    plt.title('Phân bố số lượng ảnh theo lớp')
    plt.xlabel('Lớp')
    plt.ylabel('Số lượng ảnh')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('class_distribution.png')
    plt.close()

    # Nén dataset đã làm sạch
    zip_path = os.path.join(os.path.dirname(output_dir), 'dataset_clean.zip')
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
    print(f"Đã nén và lưu file zip đã làm sạch vào: {zip_path}")

def main():
    print("Bắt đầu làm sạch dữ liệu...")
    clean_dataset()
    print("Hoàn thành làm sạch dữ liệu!")

if __name__ == "__main__":
    main()