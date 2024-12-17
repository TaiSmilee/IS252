import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, Label, Button, Radiobutton, StringVar

# Function to calculate entropy
def entropy(target_col):
    elements, counts = np.unique(target_col, return_counts=True)
    return -np.sum([(counts[i] / np.sum(counts)) * np.log2(counts[i] / np.sum(counts)) for i in range(len(elements))])

# Function to calculate information gain
def info_gain(data, split_attribute_name, target_name="Play ball", log_output=None):
    if log_output is not None:
        log_output.insert(tk.END, f"\nTính entropy cho thuộc tính '{split_attribute_name}'\n")

    total_entropy = entropy(data[target_name])
    if log_output is not None:
        log_output.insert(tk.END, f"Entropy tổng: {total_entropy:.4f}\n")

    vals, counts = np.unique(data[split_attribute_name], return_counts=True)
    weighted_entropy = np.sum([
        (counts[i] / np.sum(counts)) * entropy(data.where(data[split_attribute_name] == vals[i]).dropna()[target_name])
        for i in range(len(vals))
    ])

    if log_output is not None:
        for i, val in enumerate(vals):
            subset_entropy = entropy(data.where(data[split_attribute_name] == val).dropna()[target_name])
            log_output.insert(tk.END, f"  - Giá trị '{val}': Entropy = {subset_entropy:.4f}\n")
        log_output.insert(tk.END, f"Weighted Entropy: {weighted_entropy:.4f}\n")

    information_gain = total_entropy - weighted_entropy

    if log_output is not None:
        log_output.insert(tk.END, f"Information Gain cho '{split_attribute_name}': {information_gain:.4f}\n")

    return information_gain

# Function to calculate Gini index
def gini_index(target_col):
    elements, counts = np.unique(target_col, return_counts=True)
    return 1 - np.sum((counts / np.sum(counts)) ** 2)

# Function to calculate Gini for a split
def gini_split(data, split_attribute_name, target_name="Play ball", log_output=None):
    """
    Tính Gini Split của một thuộc tính.
    """
    if log_output is not None:
        log_output.insert(tk.END, f"\nTính Gini cho thuộc tính '{split_attribute_name}'\n")

    vals, counts = np.unique(data[split_attribute_name], return_counts=True)
    total_gini = 0

    details = []

    for i in range(len(vals)):
        subset = data[data[split_attribute_name] == vals[i]]
        subset_gini = gini_index(subset[target_name])
        weighted_gini = (counts[i] / np.sum(counts)) * subset_gini
        total_gini += weighted_gini
        details.append(f"  - Giá trị '{vals[i]}': Gini = {subset_gini:.4f}, Weighted Gini = {weighted_gini:.4f}")

    if log_output is not None:
        log_output.insert(tk.END, "\n".join(details) + "\n")

    if log_output is not None:
        log_output.insert(tk.END, f"Gini Split tổng cho '{split_attribute_name}': {total_gini:.4f}\n")

    return total_gini

# ID3 algorithm
def ID3(data, original_data, features, target_attribute_name="Play ball", parent_node_class=None, method="gain", log_output=None):
    if len(np.unique(data[target_attribute_name])) <= 1:
        if log_output is not None:
            log_output.insert(tk.END, f"Nút lá: {np.unique(data[target_attribute_name])[0]}\n")
        return np.unique(data[target_attribute_name])[0]

    elif len(data) == 0:
        majority_class = np.unique(original_data[target_attribute_name])[
            np.argmax(np.unique(original_data[target_attribute_name], return_counts=True)[1])
        ]
        if log_output is not None:
            log_output.insert(tk.END, f"Dữ liệu rỗng. Chọn lớp cha: {majority_class}\n")
        return majority_class

    elif len(features) == 0:
        if log_output is not None:
            log_output.insert(tk.END, f"Hết thuộc tính. Chọn lớp cha: {parent_node_class}\n")
        return parent_node_class

    else:
        parent_node_class = np.unique(data[target_attribute_name])[np.argmax(np.unique(data[target_attribute_name], return_counts=True)[1])]
        if log_output is not None:
            log_output.insert(tk.END, f"\nLớp cha: {parent_node_class}\n")

        if method == "gain":
            item_values = [info_gain(data, feature, target_attribute_name, log_output) for feature in features]
        else:
            item_values = [-gini_split(data, feature, target_attribute_name, log_output) for feature in features]

        best_feature_index = np.argmax(item_values)
        best_feature = features[best_feature_index]

        if log_output is not None:
            log_output.insert(tk.END, f"Chọn thuộc tính tốt nhất: {best_feature}\n")

        tree = {best_feature: {}}
        features = [i for i in features if i != best_feature]

        for value in np.unique(data[best_feature]):
            value_subdata = data.where(data[best_feature] == value).dropna()
            if log_output is not None:
                log_output.insert(tk.END, f"\nXử lý nhánh {best_feature} = {value}\n")

            subtree = ID3(value_subdata, original_data, features, target_attribute_name, parent_node_class, method, log_output)
            tree[best_feature][value] = subtree

        return tree

# Function to visualize tree using tkinter.Canvas
def visualize_tree_tkinter(tree):
    def calculate_spacing(tree):
        """ Đệ quy tính số lượng nút lá để xác định khoảng cách. """
        if not isinstance(tree, dict):
            return 1  # Một nút lá
        return sum(calculate_spacing(subtree) for subtree in tree.values())

    def draw_tree(canvas, tree, x, y, x_spacing, y_spacing, depth=0):
        """ Hàm đệ quy để vẽ cây với khoảng cách phù hợp """
        if not isinstance(tree, dict):
            leaf_color = "green" if tree == "Yes" else "red"
            canvas.create_text(x, y, text=str(tree), font=("Arial", 12, "bold"), fill=leaf_color)
            return

        feature = list(tree.keys())[0]
        branches = tree[feature]

        canvas.create_text(x, y, text=feature, font=("Arial", 14, "bold"), fill="blue")

        total_leaves = sum(calculate_spacing(subtree) for subtree in branches.values())
        start_x = x - (x_spacing * total_leaves) / 2  

        for branch_value, subtree in branches.items():
            leaves_count = calculate_spacing(subtree)
            child_x = start_x + (x_spacing * leaves_count) / 2
            child_y = y + y_spacing

            canvas.create_line(x, y + 10, child_x, child_y - 10, arrow=tk.LAST)

            text_x = (x + child_x) / 2
            text_y = (y + child_y) / 2 - 10  
            canvas.create_text(text_x, text_y, text=str(branch_value), font=("Arial", 10, "bold"), fill="black")

            draw_tree(canvas, subtree, child_x, child_y, x_spacing / 1.5, y_spacing, depth + 1)

            start_x += x_spacing * leaves_count

    tree_window = tk.Tk()
    tree_window.title("Decision Tree Visualization")

    canvas_width = 800  
    canvas_height = 600
    canvas = tk.Canvas(tree_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    root_x = canvas_width // 2
    root_y = 50
    initial_spacing = canvas_width // 6  
    y_spacing = 80  

    draw_tree(canvas, tree, root_x, root_y, initial_spacing, y_spacing)

    tree_window.mainloop()
# GUI Application
def main():
    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            label_file_status.config(text=f"Đã chọn file: {file_path}")
            global df
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                label_file_status.config(text=f"Lỗi khi đọc file: {e}")
                df = None

    def process_data():
        result_text.delete(1.0, tk.END)
        if 'df' not in globals() or df is None:
            result_text.insert(tk.END, "Chưa tải file hoặc file bị lỗi.\n")
            return

        method = method_var.get()
        target_name = "Play ball"

        if target_name not in df.columns:
            result_text.insert(tk.END, "\nCần có cột \"Play ball\" trong tệp dữ liệu.\n")
            return

        features = [col for col in df.columns if col != target_name]
        result_text.insert(tk.END, f"\nTính toán sử dụng: {method.capitalize()}\n")

        global tree
        tree = ID3(df, df, features, target_name, method=method, log_output=result_text)
        result_text.insert(tk.END, f"\nCây quyết định đã được tạo thành công. Nhấn \"Hiển thị hình cây\" để xem.\n")

    def show_tree():
        if 'tree' not in globals() or tree is None:
            result_text.insert(tk.END, "Cây quyết định chưa được tạo. Hãy nhấn \"Xử lý\" trước.\n")
        else:
            visualize_tree_tkinter(tree)

    root = tk.Tk()
    root.title("Decision Tree Visualization")

    method_var = StringVar(value="gain")

    frame = tk.Frame(root)
    frame.pack(pady=10, padx=10)

    label_file_status = Label(frame, text="Chưa tải file")
    label_file_status.grid(row=0, column=1, padx=5)

    Button(frame, text="Tải file", command=load_file).grid(row=0, column=0, padx=5)

    Radiobutton(frame, text="Information Gain", variable=method_var, value="gain").grid(row=1, column=0, padx=5)
    Radiobutton(frame, text="Gini Index", variable=method_var, value="gini").grid(row=1, column=1, padx=5)

    Button(frame, text="Xử lý", command=process_data).grid(row=2, column=0, columnspan=2, pady=10)

    result_text = tk.Text(root, width=80, height=20)
    result_text.pack(pady=10, padx=10)

    Button(root, text="Hiển thị hình cây quyết định", command=show_tree).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
