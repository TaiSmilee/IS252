import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from collections import defaultdict

data = None
yes_probs = None
no_probs = None
features = None

# Hàm tính xác suất (không làm trơn Laplace)
def calculate_probabilities_no_smoothing(df, features, target_value):
    probabilities = defaultdict(float)
    target_df = df[df["Play ball"] == target_value]
    total = len(target_df)
    probabilities["prior"] = total / len(df)
    for feature in features:
        for value in df[feature].unique():
            count = len(target_df[target_df[feature] == value])
            probabilities[f"{feature}={value}"] = count / total if total > 0 else 0
    return probabilities

# Hàm tính xác suất (có làm trơn Laplace)
def calculate_probabilities_with_smoothing(df, features, target_value):
    probabilities = defaultdict(float)
    target_df = df[df["Play ball"] == target_value]
    total = len(target_df) 
    num_unique_target_values = len(df["Play ball"].unique())  
    probabilities["prior"] = (total + 1) / (len(df) + num_unique_target_values)
    for feature in features:
        unique_values = df[feature].unique()  
        num_unique_values = len(unique_values)  
        for value in unique_values:
            count = len(target_df[target_df[feature] == value])  
            probabilities[f"{feature}={value}"] = (count + 1) / (total + num_unique_values)
    return probabilities

# Hàm cập nhật xác suất dựa trên chế độ làm trơn
def update_probabilities():
    global yes_probs, no_probs
    if smoothing.get() == "yes":
        yes_probs = calculate_probabilities_with_smoothing(data, features, "Yes")
        no_probs = calculate_probabilities_with_smoothing(data, features, "No")
    else:
        yes_probs = calculate_probabilities_no_smoothing(data, features, "Yes")
        no_probs = calculate_probabilities_no_smoothing(data, features, "No")

# Hàm xử lý khi tải file
def open_file():
    global data, yes_probs, no_probs, features
    file_path = filedialog.askopenfilename(
        title="Tải file dữ liệu",
        filetypes=(("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        try:
            data = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
            required_columns = ["Outlook", "Temperature", "Humidity", "Wind", "Play ball"]
            if not all(col in data.columns for col in required_columns):
                raise ValueError(f"File phải chứa các cột: {', '.join(required_columns)}")
            features = ["Outlook", "Temperature", "Humidity", "Wind"]
            update_probabilities()
            label_file_status.config(text=f"\u0110ã chọn file: {file_path.split('/')[-1]}")
            create_input_fields()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

# Hàm dự đoán
def make_prediction():
    update_probabilities()  
    sample = {
        "Outlook": weather_var.get(),
        "Temperature": temp_var.get(),
        "Humidity": humidity_var.get(),
        "Wind": wind_var.get()
    }
    sample = {k: v for k, v in sample.items() if v != "Không chọn"}

    prior_yes = yes_probs["prior"]
    prior_no = no_probs["prior"]

    yes_likelihood = prior_yes
    no_likelihood = prior_no

    yes_steps = [f"{prior_yes:.3f}"]
    no_steps = [f"{prior_no:.3f}"]

    for feature, value in sample.items():
        yes_prob = yes_probs.get(f"{feature}={value}", 1 / (len(data) + len(data[feature].unique())))
        no_prob = no_probs.get(f"{feature}={value}", 1 / (len(data) + len(data[feature].unique())))

        yes_likelihood *= yes_prob
        no_likelihood *= no_prob

        yes_steps.append(f"{yes_prob:.3f}")
        no_steps.append(f"{no_prob:.3f}")

    result_text = f"=== Xác suất tiên nghiệm ===\n"
    result_text += f"P(Yes) = {prior_yes:.3f}\n"
    result_text += f"P(No) = {prior_no:.3f}\n\n"

    result_text += "=== Tính xác suất có điều kiện ===\n"
    result_text += f"P(Yes|{', '.join(sample.values())}) = {' * '.join(yes_steps)} = {yes_likelihood:.5f}\n"
    result_text += f"P(No|{', '.join(sample.values())}) = {' * '.join(no_steps)} = {no_likelihood:.5f}\n"

    prediction = "Yes" if yes_likelihood > no_likelihood else "No"
    result_text += f"\n ==> Dự đoán: {prediction}"

    result_label.config(text=result_text)


# Hàm tạo giao diện nhập liệu
def create_input_fields():
    for widget in frame_inputs.winfo_children():
        widget.destroy()

    global weather_var, temp_var, humidity_var, wind_var

    input_labels = ["Outlook", "Temperature", "Humidity", "Wind"]
    variables = [weather_var, temp_var, humidity_var, wind_var] = [tk.StringVar(value="Không chọn") for _ in range(4)]
    values = [["Không chọn"] + list(data[feature].unique()) for feature in features]

    for i, (label, var, val) in enumerate(zip(input_labels, variables, values)):
        ttk.Label(frame_inputs, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky="w")
        ttk.Combobox(frame_inputs, textvariable=var, values=val).grid(row=i, column=1, padx=10, pady=5)

    ttk.Label(frame_inputs, text="Làm trơn Laplace:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    tk.Radiobutton(frame_inputs, text="Có", variable=smoothing, value="yes", command=update_probabilities).grid(row=4, column=1, sticky="w")
    tk.Radiobutton(frame_inputs, text="Không", variable=smoothing, value="no", command=update_probabilities).grid(row=5, column=1, sticky="w")

    btn_predict.grid(row=6, column=0, columnspan=2, pady=10)
    result_label.grid(row=7, column=0, columnspan=2, pady=5)


# Giao diện chính

root = tk.Tk()
root.title("Dự đoán 'Play ball' bằng Naïve Bayes")
root.geometry("500x500")
smoothing = tk.StringVar(value="no")

frame_inputs = ttk.Frame(root)
frame_inputs.grid(pady=20, padx=20)

btn_open = ttk.Button(root, text="Chọn file dữ liệu", command=open_file)
btn_open.grid(row=0, column=0, pady=10, padx=10)
label_file_status = tk.Label(root, text="Chưa chọn file", font=("Arial", 10))
label_file_status.grid(row=0, column=1, padx=10, pady=10)

btn_predict = ttk.Button(root, text="Chạy thuật toán", command=make_prediction)
result_label = tk.Label(root, text="", font=("Arial", 10))

frame_inputs.grid(row=1, column=0, columnspan=2)

root.mainloop()
