import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog

def initialize_partition_matrix(n_samples: int, n_clusters: int):
    """
    Khởi tạo ma trận phân hoạch dạng ma trận chéo, với các đường chéo là 1.
    Nếu số cụm nhỏ hơn số mẫu, các hàng còn lại sẽ có giá trị 1.
    """
    partition_matrix = np.zeros((n_samples, n_clusters))
    for i in range(min(n_samples, n_clusters)):
        partition_matrix[i, i] = 1
    # Các hàng còn lại sẽ gán 1 cho cụm cuối cùng
    if n_samples > n_clusters:
        for i in range(n_clusters, n_samples):
            partition_matrix[i, -1] = 1
    return partition_matrix

def calculate_centroids(data: np.ndarray, partition_matrix: np.ndarray):
    """
    Tính vector trọng tâm từ ma trận phân hoạch.
    """
    n_attrs = data.shape[1]
    n_clusters = partition_matrix.shape[1]
    centroids = np.zeros((n_attrs, n_clusters))

    for j in range(n_clusters):
        indices = np.where(partition_matrix[:, j] == 1)[0]
        if len(indices) > 0:
            centroids[:, j] = np.mean(data[indices], axis=0)
    return centroids

def calculate_partition_matrix(data: np.ndarray, centroids: np.ndarray):
    """
    Tính ma trận phân hoạch dựa trên khoảng cách Euclidean giữa dữ liệu và các vector trọng tâm.
    """
    n_samples = data.shape[0]
    n_clusters = centroids.shape[1]
    partition_matrix = np.zeros((n_samples, n_clusters))

    for i in range(n_samples):
        distances = [np.linalg.norm(data[i] - centroids[:, j]) for j in range(n_clusters)]
        min_index = np.argmin(distances)
        partition_matrix[i, min_index] = 1  # Gán vào cụm có khoảng cách nhỏ nhất

    return partition_matrix

def kohonen_algorithm(data: pd.DataFrame, n_clusters: int, learning_rate: float, epochs: int, text_box):
    np.random.seed(42)
    
    # Tách nhãn và vector thuộc tính
    labels = data.iloc[:, 0]  # Cột đầu tiên là nhãn
    input_vectors = data.iloc[:, 1:].values  # Các cột còn lại là vector thuộc tính
    n_samples, n_attrs = input_vectors.shape

    # Khởi tạo ma trận phân hoạch ban đầu
    partition_matrix = initialize_partition_matrix(n_samples, n_clusters)
    text_box.insert(tk.END, "Bước 0 - Ma trận phân hoạch khởi tạo:\n")
    text_box.insert(tk.END, f"{partition_matrix}\n")

    # Tính vector trọng tâm ban đầu
    weights = calculate_centroids(input_vectors, partition_matrix)
    text_box.insert(tk.END, "Bước 0 - Vector trọng tâm khởi tạo:\n")
    text_box.insert(tk.END, f"{weights}\n")

    # Bán kính cố định là 0
    radius = 0.0

    # Lặp qua các epoch
    for epoch in range(epochs):
        text_box.insert(tk.END, f"\nEpoch {epoch + 1}:\n")

        # Tính ma trận phân hoạch mới
        partition_matrix = calculate_partition_matrix(input_vectors, weights)
        text_box.insert(tk.END, f"Ma trận phân hoạch:\n{partition_matrix}\n")

        # Cập nhật trọng số (vector trọng tâm)
        weights = calculate_centroids(input_vectors, partition_matrix)
        text_box.insert(tk.END, f"Vector trọng tâm:\n{weights}\n")

        # Hiển thị thông tin trong epoch
        text_box.insert(tk.END, f"Tốc độ học: {learning_rate:.4f}, Bán kính: {radius:.4f}\n")

    # Hiển thị kết quả cụm cuối cùng
    text_box.insert(tk.END, "\nKết quả phân cụm cuối cùng:\n")
    clusters = {i: [] for i in range(n_clusters)}
    for i, row in enumerate(partition_matrix):
        cluster_idx = np.argmax(row)
        clusters[cluster_idx].append(labels.iloc[i])

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
        learning_rate = 0.4  # Tốc độ học
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
