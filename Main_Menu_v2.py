from tkinter import *
import subprocess

def run_script(script_name):
    try:
        subprocess.Popen(['python', script_name])
    except Exception as e:
        print(f"Error: {e}")

def show_frame(frame):
    frame.tkraise()

root = Tk()
root.title('DATA MINING')
root.configure(bg='#1C2833')

# Nhãn tiêu đề
title_label = Label(
    root,
    text='CÁC THUẬT TOÁN KHAI THÁC DỮ LIỆU',
    fg='#FDFEFE',
    bg='#1C2833',
    font=('Cambria', 20, 'bold'),
    pady=4
)
title_label.pack(pady=2)

# Tạo khung chứa các frame con với khoảng cách hai bên
container = Frame(root, bg='#1C2833')
container.pack(fill=BOTH, expand=True)
container.grid_columnconfigure(0, weight=1)
container.grid_columnconfigure(2, weight=1)

inner_frame = Frame(container, bg='#1C2833')
inner_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

main_frame = Frame(inner_frame, bg='#2E4053', bd=5, relief=RIDGE)
main_frame.grid(row=0, column=0, sticky='nsew')

# Tạo các nhóm thuật toán trong main_frame
def create_algorithm_group(parent, title, buttons):
    section_frame = LabelFrame(
        parent,
        text=title,
        bg='#34495E',
        fg='#ECF0F1',
        font=('Cambria', 15, 'bold'),
        relief=RIDGE,
        bd=2
    )
    section_frame.pack(fill=X, pady=10, padx=10)

    button_frame = Frame(section_frame, bg='#34495E')
    button_frame.pack(pady=10)

    # Chia đều các nút trong khung
    for i, (btn_text, btn_color, script_name) in enumerate(buttons):
        Button(
            button_frame,
            text=btn_text,
            font=('Cambria', 14, 'bold'),
            bg=btn_color,
            fg='white',
            relief=RAISED,
            width=20,
            command=lambda script=script_name: run_script(script)
        ).grid(row=0, column=i, padx=10, pady=10)

# Tạo nhóm thuật toán trong main_frame
create_algorithm_group(main_frame, 'Xử lý dữ liệu', [('Xử lý dữ liệu', '#70635f', '.py')])
create_algorithm_group(main_frame, 'Thuật toán Apriori', [('Apriori', '#1ABC9C', 'Apriori.py')])
create_algorithm_group(main_frame, 'Thuật toán tập thô', [('Tập thô', '#6699FF', 'Rough_set.py')])
create_algorithm_group(
    main_frame,
    'Thuật toán phân lớp',
    [('ID3 - Cây quyết định', '#3498DB', '.py'), ('Naive Bayes', '#3498DB', '.py')]
)
create_algorithm_group(
    main_frame,
    'Thuật toán gom cụm',
    [('K-means', '#E67E22', '.py'), ('Mạng Kohonen', '#E67E22', '.py')]
)

# Footer
footer_frame = Frame(root, bg='#1C2833', pady=10)
footer_frame.pack(fill=X)

footer_left = Label(
    footer_frame,
    text='22522566 - Nguyễn Hữu Tài\n22521593 - Phạm Nguyên Tú',
    bg='#1C2833',
    fg='#FDFEFE',
    font=('Cambria', 12, 'italic'),
    justify=LEFT
)
footer_left.pack(side=LEFT, padx=20)

footer_right = Label(
    footer_frame,
    text='22521014 - Hoàng Minh Nhật\n22521052 - Nguyễn Ngô Hoài Như',
    bg='#1C2833',
    fg='#FDFEFE',
    font=('Cambria', 12, 'italic'),
    justify=RIGHT
)
footer_right.pack(side=RIGHT, padx=20)

footer_teacher = Label(
    footer_frame,
    text='Giáo viên hướng dẫn: Ths. Mai Xuân Hùng',
    bg='#1C2833',
    fg='#FDFEFE',
    font=('Cambria', 12, 'italic'),
    anchor='center'
)
footer_teacher.pack(pady=10)

# Hiển thị main_frame đầu tiên
show_frame(main_frame)

# Chạy vòng lặp chính
root.mainloop()
