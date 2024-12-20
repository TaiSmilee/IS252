import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, Label, Button, Entry, Text, END, E

data = None
def open_file():
    global data
    file_path = filedialog.askopenfilename(title="Chọn file dữ liệu", filetypes=[("Excel files", "*.xlsx")])
    
    if file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
        status_label.config(text=f"Đã chọn file: {file_path.split('/')[-1]}")

        if data.shape[1] >= 2:
            col1_entry.delete(0, END)
            col2_entry.delete(0, END)
            col1_entry.insert(0, data.columns[0])
            col2_entry.insert(0, data.columns[1])
        else:
            status_label.config(text="File không đủ 2 cột để tính toán.", fg="red")
    else:
        status_label.config(text="Định dạng file không được hỗ trợ. Vui lòng chọn file .xlsx", fg="red")

def calculate_correlation(x, y):
    n = len(x)  
    # Tính giá trị trung bình 
    mean_x = np.mean(x)  
    mean_y = np.mean(y)  

    # Tính tổng bình phương và tích
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x ** 2)
    sum_y2 = np.sum(y ** 2)

    # Tính giá trị trung bình các bình phương
    mean_xy = sum_xy / n
    mean_x2 = sum_x2 / n
    mean_y2 = sum_y2 / n

    # Tính phương sai
    variance_x = mean_x2 - mean_x ** 2
    variance_y = mean_y2 - mean_y ** 2

    # Tính độ lệch chuẩn
    std_x = np.sqrt(variance_x)
    std_y = np.sqrt(variance_y)

    # Tính hệ số tương quan
    covariance_xy = mean_xy - mean_x * mean_y
    correlation_coefficient = covariance_xy / (std_x * std_y)

    return {
        "correlation": correlation_coefficient,
        "variance_x": variance_x,
        "variance_y": variance_y,
        "mean_x": mean_x,
        "mean_y": mean_y,
        "sum_xy": sum_xy,
        "sum_x2": sum_x2,
        "sum_y2": sum_y2,
        "std_x": std_x,
        "std_y": std_y,
    }

def calculate():
    global data

    if data is None:
        result_text.delete(1.0, END)
        result_text.insert(END, "Vui lòng chọn file dữ liệu trước.")
        return

    column1 = col1_entry.get()
    column2 = col2_entry.get()

    if column1 not in data.columns or column2 not in data.columns:
        result_text.delete(1.0, END)
        result_text.insert(END, "Tên cột không hợp lệ. Vui lòng kiểm tra và thử lại.")
        return

    try:
        if data[column1].dtype == 'object':
            x = pd.to_numeric(data[column1].str.replace(',', '.'), errors='coerce').dropna()
        else:
            x = pd.to_numeric(data[column1], errors='coerce').dropna()

        if data[column2].dtype == 'object':
            y = pd.to_numeric(data[column2].str.replace(',', '.'), errors='coerce').dropna()
        else:
            y = pd.to_numeric(data[column2], errors='coerce').dropna()

        if x.empty or y.empty:
            result_text.delete(1.0, END)
            result_text.insert(END, "Dữ liệu không đủ giá trị hợp lệ để tính toán.")
            return

        valid_index = x.index.intersection(y.index)
        x = x.loc[valid_index]
        y = y.loc[valid_index]

        if len(x) == 0 or len(y) == 0:
            result_text.delete(1.0, END)
            result_text.insert(END, "Dữ liệu không đủ để tính toán.")
            return

        results = calculate_correlation(x, y)

        result_text.delete(1.0, END)
        result_text.tag_configure('bold', font=('Arial', 10, 'bold'))

        result_text.insert(END, f"Số phần tử n: {len(x)}\n")
        result_text.insert(END, "Giá trị trung bình của x: ")
        result_text.insert(END, f"{results['mean_x']:.2f}\n")
        result_text.insert(END, "Giá trị trung bình của y: ")
        result_text.insert(END, f"{results['mean_y']:.2f}\n")
        result_text.insert(END, "Tổng tích (Σ x*y): ")
        result_text.insert(END, f"{results['sum_xy']:.2f}\n")
        result_text.insert(END, "Tổng bình phương (Σ x^2): ")
        result_text.insert(END, f"{results['sum_x2']:.2f}\n")
        result_text.insert(END, "Tổng bình phương (Σ y^2): ")
        result_text.insert(END, f"{results['sum_y2']:.2f}\n")
        result_text.insert(END, "Phương sai của x: ")
        result_text.insert(END, f"{results['variance_x']:.2f}\n")
        result_text.insert(END, "Phương sai của y: ")
        result_text.insert(END, f"{results['variance_y']:.2f}\n")
        result_text.insert(END, "Độ lệch chuẩn của x: ")
        result_text.insert(END, f"{results['std_x']:.2f}\n")
        result_text.insert(END, "Độ lệch chuẩn của y: ")
        result_text.insert(END, f"{results['std_y']:.2f}\n")
        result_text.insert(END, "==> Hệ số tương quan giữa x và y: ", 'bold')
        result_text.insert(END, f"{results['correlation']:.2f}\n", 'bold')

    except Exception as e:
        result_text.delete(1.0, END)
        result_text.insert(END, f"Lỗi khi xử lý dữ liệu: {str(e)}")


root = Tk()
root.title("Tính Hệ Số Tương Quan")
root.geometry("500x400")

browse_button = Button(root, text="Chọn file dữ liệu", command=open_file)
browse_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

status_label = Label(root, text="")
status_label.grid(row=1, column=0, columnspan=2)

col1_label = Label(root, text="Tên cột thứ nhất:", font=('Arial', 10, 'bold'))
col1_label.grid(row=2, column=0, padx=10, pady=10, sticky=E)
col1_entry = Entry(root, width=30)
col1_entry.grid(row=2, column=1, padx=10, pady=10)

col2_label = Label(root, text="Tên cột thứ hai:", font=('Arial', 10, 'bold'))
col2_label.grid(row=3, column=0, padx=10, pady=10, sticky=E)
col2_entry = Entry(root, width=30)
col2_entry.grid(row=3, column=1, padx=10, pady=10)

calculate_button = Button(root, text="Tính toán hệ số tương quan", command=calculate)
calculate_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

result_text = Text(root, height=10, width=50)
result_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
