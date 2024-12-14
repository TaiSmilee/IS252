import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from itertools import combinations
from typing import List, Dict, Union, Tuple, FrozenSet, Optional

def generate_frequent_itemsets(basket: pd.DataFrame, min_support: float) -> List[Tuple[FrozenSet[int], float]]:
    item_support: Dict[FrozenSet[int], float] = {}
    n_transactions: int = len(basket)

    # Tính support cho từng item
    for column in basket.columns:
        support: float = basket[column].sum() / n_transactions
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
            support: float = basket[list(candidate)].all(axis=1).sum() / n_transactions
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

            # Truy xuất antecedent_support một cách an toàn
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
        label_file_path.config(text=f"\u0110ã chọn: {file_path}")
    else:
        label_file_path.config(text="Chưa chọn file.")

def run_apriori() -> None:
    try:
        if not file_path:
            raise ValueError("Vui lòng tải lên file Excel.")
        
        df: pd.DataFrame = pd.read_excel(file_path)
        if 'order_id' not in df.columns or 'product_id' not in df.columns:
            raise ValueError("File Excel phải chứa các cột 'order_id' và 'product_id'.")

        basket: pd.DataFrame = df.groupby(['order_id', 'product_id']).size().unstack(fill_value=0)
        basket = (basket > 0).astype(int)
        print("Basket DataFrame:")
        print(basket.head())  # Kiểm tra dữ liệu

        min_supp: float = float(entry_min_supp.get())
        min_conf: float = float(entry_min_conf.get())
        if not (0 < min_supp <= 1) or not (0 < min_conf <= 1):
            raise ValueError("Giá trị min_supp và min_conf phải nằm trong khoảng (0, 1].")
        
        frequent_itemsets: List[Tuple[FrozenSet[int], float]] = generate_frequent_itemsets(basket, min_supp)
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
            text: tk.Text = tk.Text(output_window, wrap=tk.WORD, height=30, width=100)
            text.pack()
            for rule in rules:
                text.insert(tk.END, f"{rule['antecedent']} => {rule['consequence']}\n")
                text.insert(tk.END, f"Support: {rule['support']}, Confidence: {rule['confidence']}\n\n")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

# Tạo giao diện Tkinter
root: tk.Tk = tk.Tk()
root.title("Thuật toán Apriori")
root.geometry("400x300")
root.resizable(False, False)

file_path: str = ""

# Nút tải file
button_upload: tk.Button = tk.Button(root, text="Tải file Excel", command=upload_file)
button_upload.pack()

# Nhãn hiển thị đường dẫn file
label_file_path: tk.Label = tk.Label(root, text="Chưa chọn file.")
label_file_path.pack()

# Nhãn và ô nhập cho min_support
label_min_supp: tk.Label = tk.Label(root, text="Ngưỡng min_supp:")
label_min_supp.pack()
entry_min_supp: tk.Entry = tk.Entry(root)
entry_min_supp.pack()

# Nhãn và ô nhập cho min_conf
label_min_conf: tk.Label = tk.Label(root, text="Ngưỡng min_conf:")
label_min_conf.pack()
entry_min_conf: tk.Entry = tk.Entry(root)
entry_min_conf.pack()

# Nút chạy thuật toán
button_run: tk.Button = tk.Button(root, text="Chạy thuật toán", command=run_apriori)
button_run.pack()

# Chạy ứng dụng Tkinter
root.mainloop()

