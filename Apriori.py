import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from itertools import combinations
from typing import List, Dict, Union, Tuple, FrozenSet, Optional

# Tạo hàm chạy thuật toán Apriori
def generate_frequent_itemsets(matrix: pd.DataFrame, min_support: float) -> List[Tuple[FrozenSet[int], float]]:
    item_support: Dict[FrozenSet[int], float] = {}
    n_transactions: int = len(matrix)

    # Tính support cho từng item
    for column in matrix.columns:
        support: float = matrix[column].sum() / n_transactions
        if support >= min_support:
            item_support[frozenset([column])] = support

    # Tìm tập phổ biến lớn hơn
    frequent_itemsets: List[Tuple[FrozenSet[int], float]] = []
    k: int = 2
    current_itemsets: List[FrozenSet[int]] = list(item_support.keys())
    while current_itemsets:
        candidates: List[Tuple[int, ...]] = list(combinations(set().union(*current_itemsets), k))
        candidate_support: Dict[FrozenSet[int], float] = {}

        for candidate in candidates:
            candidate_set: FrozenSet[int] = frozenset(candidate)
            support: float = matrix[list(candidate)].all(axis=1).sum() / n_transactions
            if support >= min_support:
                candidate_support[candidate_set] = support

        if not candidate_support:
            break

        item_support.update(candidate_support)
        current_itemsets = list(candidate_support.keys())
        frequent_itemsets.extend(candidate_support.items())
        k += 1

    return frequent_itemsets

def generate_association_rules(frequent_itemsets: List[Tuple[FrozenSet[int], float]], min_confidence: float) -> List[Dict[str, Union[set, float]]]:
    rules: List[Dict[str, Union[set, float]]] = []
    for itemset, support in frequent_itemsets:
        if len(itemset) < 2:
            continue

        for consequence in itemset:
            antecedent: FrozenSet[int] = itemset - frozenset([consequence])
            antecedent_support: Optional[float] = next((s for i, s in frequent_itemsets if i == antecedent), None)
            if antecedent_support is None:
                continue

            confidence: float = support / antecedent_support
            if confidence >= min_confidence:
                rules.append({
                    "antecedent": set(antecedent),
                    "consequence": set([consequence]),
                    "support": support,
                    "confidence": confidence
                })

    return rules

def upload_file() -> None:
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        label_file_path.config(text=f"Đã chọn: {file_path}")
    else:
        label_file_path.config(text="Chưa chọn file.")

def run_apriori() -> None:
    try:
        if not file_path:
            raise ValueError("Vui lòng tải lên file Excel.")
        
        df: pd.DataFrame = pd.read_excel(file_path)
        if 'order_id' not in df.columns or 'product_id' not in df.columns:
            raise ValueError("File Excel phải chứa các cột 'order_id' và 'product_id'.")

        matrix: pd.DataFrame = df.groupby(['order_id', 'product_id']).size().unstack(fill_value=0)
        matrix = (matrix > 0).astype(int)
        print("Basket DataFrame:")
        print(matrix.head())  # Kiểm tra dữ liệu

        min_supp: float = float(entry_min_supp.get())
        min_conf: float = float(entry_min_conf.get())
        if not (0 < min_supp <= 1) or not (0 < min_conf <= 1):
            raise ValueError("min_supp và min_conf phải nằm trong khoảng (0, 1].")
        
        frequent_itemsets: List[Tuple[FrozenSet[int], float]] = generate_frequent_itemsets(matrix, min_supp)
        print("Frequent Itemsets:")
        print(frequent_itemsets)  # Kiểm tra đầu ra

        rules: List[Dict[str, Union[set, float]]] = generate_association_rules(frequent_itemsets, min_conf)
        print("Association Rules:")
        print(rules)  # Kiểm tra đầu ra

        if not rules:
            messagebox.showinfo("Kết quả", "Không tìm thấy luật kết hợp nào thỏa mãn.")
        else:
            output_window: tk.Toplevel = tk.Toplevel(root)
            output_window.title("Kết quả")
            text: tk.Text = tk.Text(output_window, wrap=tk.WORD, height=30, width=80, bg="#1C2833", fg="white")
            text.pack()
            for rule in rules:
                text.insert(tk.END, f"{rule['antecedent']} => {rule['consequence']}\n")
                text.insert(tk.END, f"Support: {rule['support']}, Confidence: {rule['confidence']}\n\n")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

# Tạo giao diện Tkinter
root: tk.Tk = tk.Tk()
root.title("Thuật toán Apriori")
root.geometry("500x400")
root.configure(bg="#1C2833")

file_path: str = ""

# Tiêu đề
title_label = tk.Label(root, text="THUẬT TOÁN APRIORI", font=("Cambria", 18, "bold"), bg="#1C2833", fg="white")
title_label.pack(pady=10)

# Nút tải file
button_upload = tk.Button(root, text="Tải file Excel", command=upload_file, bg="#2E4053", fg="white", font=("Cambria", 12))
button_upload.pack(pady=5)

# Đường dẫn file
label_file_path = tk.Label(root, text="Chưa chọn file.", bg="#1C2833", fg="white", font=("Cambria", 10))
label_file_path.pack(pady=5)

# Min Support Input
label_min_supp = tk.Label(root, text="Ngưỡng min_supp:", bg="#1C2833", fg="white", font=("Cambria", 12))
label_min_supp.pack(pady=5)
entry_min_supp = tk.Entry(root, font=("Cambria", 12), bg="#2E4053", fg="white", justify="center")
entry_min_supp.pack()

# Min Confidence Input
label_min_conf = tk.Label(root, text="Ngưỡng min_conf:", bg="#1C2833", fg="white", font=("Cambria", 12))
label_min_conf.pack(pady=5)
entry_min_conf = tk.Entry(root, font=("Cambria", 12), bg="#2E4053", fg="white", justify="center")
entry_min_conf.pack()

# Nút chạy thuật toán
button_run = tk.Button(root, text="Chạy thuật toán", command=run_apriori, bg="#2E4053", fg="white", font=("Cambria", 12, "bold"))
button_run.pack(pady=20)

# Chạy ứng dụng
root.mainloop()

