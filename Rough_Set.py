import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from itertools import combinations
from typing import Set, Dict, List, Tuple


def generate_discernibility_matrix(data: pd.DataFrame) -> Dict[Tuple[int, int], Set[str]]:
    n = len(data)
    attributes = list(data.columns[:-1])  # Bỏ cột quyết định
    decision_column = data.columns[-1]
    discernibility_matrix = {}

    for i, j in combinations(range(n), 2):
        if data.iloc[i][decision_column] != data.iloc[j][decision_column]:  # Chỉ xét cặp có quyết định khác nhau
            diff_attributes = {attr for attr in attributes if data.iloc[i][attr] != data.iloc[j][attr]}
            discernibility_matrix[(i, j)] = diff_attributes

    return discernibility_matrix


def check_reduct_validity(reduct: Set[str], matrix: Dict[Tuple[int, int], Set[str]]) -> bool:
    for attributes in matrix.values():
        if not any(attr in reduct for attr in attributes):
            return False
    return True


def find_all_reducts(matrix: Dict[Tuple[int, int], Set[str]], all_attributes: Set[str]) -> List[Set[str]]:
    reducts = []
    for size in range(1, len(all_attributes) + 1):
        for subset in combinations(all_attributes, size):
            subset_set = set(subset)
            if check_reduct_validity(subset_set, matrix):
                # Loại bỏ các rút gọn không tối thiểu
                if not any(existing.issubset(subset_set) for existing in reducts):
                    reducts.append(subset_set)
    return reducts


def rough_set_reduction(data: pd.DataFrame) -> List[Set[str]]:
    discernibility_matrix = generate_discernibility_matrix(data)
    all_attributes = set(data.columns[:-1])  # Bỏ cột quyết định
    reducts = find_all_reducts(discernibility_matrix, all_attributes)
    return reducts


def load_file() -> None:
    filepath: str = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not filepath:
        return
    try:
        # Đọc file Excel
        data: pd.DataFrame = pd.read_excel(filepath)
        if data.empty:
            raise ValueError("File Excel không có dữ liệu.")
        
        # Hiển thị dữ liệu đầu vào
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "Dữ liệu đầu vào:\n")
        text_box.insert(tk.END, data.to_string(index=False))
        
        # Thực hiện thuật toán tập thô
        reducts = rough_set_reduction(data)

        # Hiển thị tất cả các tập rút gọn
        text_box.insert(tk.END, "\n\nTất cả các tập rút gọn:\n")
        for i, reduct in enumerate(reducts, start=1):
            text_box.insert(tk.END, f"Rút gọn {i}: {', '.join(reduct)}\n")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xử lý file: {e}")


# Tạo giao diện Tkinter
root: tk.Tk = tk.Tk()
root.title("Thuật toán tập thô")
root.geometry("500x400")
root.configure(bg="#1C2833")

# Nút tải file
load_button: tk.Button = tk.Button(root, text="Tải file Excel", command=load_file, width=20, bg="#2E4053", fg="white", font=("Cambria", 12))
load_button.pack(pady=10)

# Text box hiển thị kết quả
text_box: tk.Text = tk.Text(root, wrap=tk.WORD, width=80, height=20, bg="#1C2833", fg="white")
text_box.pack(padx=10, pady=10)

# Bắt đầu chương trình
root.mainloop()
