import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def kohonen_algorithm(data: pd.DataFrame, n_clusters: int, learning_rate: float, epochs: int, text_box):
    np.random.seed(42)
    
    # Tách nhãn và vector thuộc tính
    labels = data.iloc[:, 0]  # Cột đầu tiên là nhãn
    input_vectors = data.iloc[:, 1:].values  # Các cột còn lại là vector thuộc tính
    n_samples, n_attrs = input_vectors.shape

    # Khởi tạo trọng số ngẫu nhiên cho các neurons (cụm)
    weights = np.random.rand(n_clusters, n_attrs) * np.max(input_vectors, axis=0)
    text_box.insert(tk.END, "Bước 0 - Vector trọng số khởi tạo:\n")
    text_box.insert(tk.END, f"{weights}\n")

    # Lặp qua các epoch
    for epoch in range(epochs):
        text_box.insert(tk.END, f"\nEpoch {epoch + 1}:\n")
        text_box.insert(tk.END, f"Tốc độ học: {learning_rate:.4f}\n")
        
        for i, x in enumerate(input_vectors):
            # Tính khoảng cách Euclidean từ vector x đến các neurons
            distances = np.linalg.norm(weights - x, axis=1)
            winner_idx = np.argmin(distances)  # Chọn neuron gần nhất

            # Cập nhật trọng số của neuron thắng
            weights[winner_idx] += learning_rate * (x - weights[winner_idx])
            text_box.insert(tk.END, f"Vector {i+1} cập nhật neuron {winner_idx+1}:\n")
            text_box.insert(tk.END, f"{weights}\n")

        # Giảm tốc độ học sau mỗi epoch
        learning_rate /= 2

        # Hiển thị trọng số sau mỗi epoch
        text_box.insert(tk.END, f"Vector trọng số sau Epoch {epoch + 1}:\n")
        text_box.insert(tk.END, f"{weights}\n")

    # Gán cụm cho từng vector dữ liệu
    text_box.insert(tk.END, "\nKết quả phân cụm cuối cùng:\n")
    clusters = {i: [] for i in range(n_clusters)}
    for i, x in enumerate(input_vectors):
        distances = np.linalg.norm(weights - x, axis=1)
        winner_idx = np.argmin(distances)
        clusters[winner_idx].append(labels.iloc[i])

    for cluster_idx, items in clusters.items():
        if items:
            text_box.insert(tk.END, f"Cụm {cluster_idx + 1}: {', '.join(map(str, items))}\n")

def run_kohonen():
    # Tạo giao diện tkinter
    root = tk.Tk()
    root.title("Thuật toán Kohonen")
    root.geometry("600x600")

    # Textbox hiển thị kết quả
    text_box = tk.Text(root, wrap=tk.WORD, width=70, height=30)
    text_box.pack(pady=10)

    # Frame nhập thông tin
    input_frame = tk.Frame(root)
    input_frame.pack(pady=5)

    # Nhãn và ô nhập số cụm
    tk.Label(input_frame, text="Số lượng nhóm cần chia:").pack(side=tk.LEFT)
    cluster_entry = tk.Entry(input_frame, width=5)
    cluster_entry.pack(side=tk.LEFT, padx=5)

    def load_data():
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not filepath:
            return None
        try:
            data = pd.read_excel(filepath)
            return data
        except Exception as e:
            text_box.insert(tk.END, f"Lỗi khi tải file: {e}\n")
            return None

    def start_algorithm():
        try:
            n_clusters = int(cluster_entry.get())
            if n_clusters <= 0:
                raise ValueError("Số cụm phải là số nguyên dương.")
        except ValueError:
            text_box.insert(tk.END, "Lỗi: Vui lòng nhập số cụm hợp lệ (số nguyên dương).\n")
            return

        data = load_data()
        if data is None:
            return

        # Thông số tham số
        learning_rate = 0.4  # Tốc độ học ban đầu
        epochs = 5  # Số lần lặp

        # Xóa nội dung cũ
        text_box.delete(1.0, tk.END)
        # Chạy thuật toán Kohonen
        kohonen_algorithm(data, n_clusters, learning_rate, epochs, text_box)

    # Nút tải dữ liệu và bắt đầu
    load_button = tk.Button(root, text="Tải dữ liệu Excel", command=start_algorithm)
    load_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_kohonen()
