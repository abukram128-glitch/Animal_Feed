import tkinter as tk
import html
import sqlite3
import hashlib
import os
import logging

# ==========================================
# 1. إعدادات السجلات الأمنية
# ==========================================
logging.basicConfig(
    filename='app_secure_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==========================================
# 2. قاموس النصوص البرمجية الموصولة والمستقيمة
# ==========================================
def get_perfect_arabic_msg(text_key: str, dynamic_name="") -> str:
    """
    هذه الدالة تعيد العبارات بحروف موصولة جاهزة ومشكلة يدوياً 
    لتخطي عيوب محرك النصوص في أندرويد وتضمن استقامتها تماماً.
    """
    messages = {
        "all_fields": "ﻳﺠﺐ ﻣﻞﺀ ﺟﻤﻴﻊ  crappy اﻟﺤﻘﻮﻝ", # "يجب ملء جميع الحقول" بأحرف موصولة نظامية
        "all_fields_fixed": "ﻳﺠﺐ ﻣﻞﺀ ﺟﻤﻴﻊ  crappy اﻟﺤﻘﻮﻝ",
        "duplicate": "اﺳﻢ اﻟﻤﺴﺘﺨﺪﻡ ﺃﻭ اﻟﺒﺮﻳﺪ ﻣﺴﺠﻞ ﻣﺴﺒﻘﺎً", # "اسم المستخدم أو البريد مسجل مسبقاً" موصولة
        "wrong_login": "اﻟﺒﺮﻳﺪ اﻹﻟﻜﺘﺮﻭﻧﻲ ﺃﻭ ﻛﻠﻤﺔ اﻟﻤﺮﻭﺭ ﻏﻴﺮ ﺻﺤﻴﺤﺔ", # "البريد الإلكتروني أو كلمة المرور غير صحيحة"
        "unexpected_error": "ﻋﺬﺭاً، ﺣﺪﺙ ﺧﻄﺄ ﻏﻴﺮ ﻣﺘﻮﻗﻊ ﻓﻲ اﻟﻨﻈﺎﻡ" # "عذراً، حدث خطأ غير متوقع في النظام"
    }
    
    # نصوص بديلة لضمان جودة الاتصال على كافة شاشات أندرويد
    if text_key == "duplicate":
        return "اﺳﻢ اﻟﻤﺴﺘﺨﺪﻡ ﺃﻭ اﻟﺒﺮﻳﺪ ﻣﺴﺠﻞ ﻣﺴﺒﻘﺎً"
    elif text_key == "all_fields":
        return "ﻳﺠﺐ ﻣﻞﺀ ﺟﻤﻴﻊ اﻟﺤﻘﻮﻝ"
    elif text_key == "wrong_login":
        return "اﻟﺒﺮﻳﺪ اﻹﻟﻜﺘﺮﻭﻧﻲ ﺃﻭ ﻛﻠﻤﺔ اﻟﻤﺮﻭﺭ ﻏﻴﺮ ﺻﺤﻴﺤﺔ"
    elif text_key == "unexpected_error":
        return "ﻋﺬﺭاً ﺣﺪﺙ ﺧﻄﺄ ﻏﻴﺮ ﻣﺘﻮﻗﻊ ﻓﻲ اﻟﻨﻈﺎﻡ"
    elif text_key == "register_success":
        return f"{dynamic_name} ﺗﻢ ﺗﺴﺠﻴﻞ اﻟﺤﺴﺎﺏ ﺑﺄﻣﺎﻥ ﺑﻨﺠﺎﺡ"
    elif text_key == "login_success":
        return f"ﻣﺮﺣﺒﺎً {dynamic_name} ﺗﻢ ﺗﺴﺠﻴﻞ اﻟﺪﺧﻮﻝ ﺑﺄﻣﺎﻥ"
        
    return text_key

# ==========================================
# 3. صندوق التنبيه الداخلي المدمج
# ==========================================
def display_internal_msg(message_key: str, is_error=True, dynamic_name=""):
    embedded_msg_box.pack_forget()
    
    bg_color = "#f2dede" if is_error else "#dff0d8"
    fg_color = "#a94442" if is_error else "#3c763d"
    border_color = "#ebccd1" if is_error else "#d6e9c6"
    
    embedded_msg_box.configure(bg=bg_color, highlightbackground=border_color, highlightcolor=border_color)
    
    # جلب النص الموصول الجاهز للعرض المستقر
    final_text = get_perfect_arabic_msg(message_key, dynamic_name)
    
    embedded_msg_label.configure(
        text=final_text, 
        fg=fg_color, 
        bg=bg_color, 
        font=("Arial", 12, "bold")
    )
    
    embedded_msg_box.pack(fill=tk.X, padx=15, pady=12, before=fields_frame)

def hide_internal_msg():
    embedded_msg_box.pack_forget()

# ==========================================
# 4. معالجة البيانات وإدارة قاعدة البيانات
# ==========================================
def sanitize_input(user_string: str) -> str:
    if not user_string:
        return ""
    return html.escape(user_string.strip())

def hash_password_securely(password: str) -> tuple:
    salt = os.urandom(32)
    pwd_hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hashed, salt

def init_db():
    conn = sqlite3.connect('secure_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash BLOB,
            password_salt BLOB
        )
    ''')
    conn.commit()
    conn.close()

def register_process():
    hide_internal_msg()
    user = sanitize_input(username_input.get())
    email = sanitize_input(email_input.get())
    pwd = password_input.get()
    
    if not user or not email or not pwd:
        display_internal_msg("all_fields", is_error=True)
        return
        
    conn = sqlite3.connect('secure_users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, user))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        display_internal_msg("duplicate", is_error=True)
        return
        
    p_hash, p_salt = hash_password_securely(pwd)
    try:
        query = "INSERT INTO users (username, email, password_hash, password_salt) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (user, email, p_hash, p_salt))
        conn.commit()
        conn.close()
        
        display_internal_msg("register_success", is_error=False, dynamic_name=user)
    except Exception as e:
        if conn:
            conn.close()
        logging.error(f"خطأ قاعدة بيانات: {str(e)}")
        display_internal_msg("unexpected_error", is_error=True)

def login_process():
    hide_internal_msg()
    email = sanitize_input(email_input.get())
    pwd = password_input.get()
    
    try:
        conn = sqlite3.connect('secure_users.db')
        cursor = conn.cursor()
        query = "SELECT username, password_hash, password_salt FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            username, stored_hash, stored_salt = row
            new_hash = hashlib.pbkdf2_hmac('sha256', pwd.encode('utf-8'), stored_salt, 100000)
            if new_hash == stored_hash:
                display_internal_msg("login_success", is_error=False, dynamic_name=username)
                return
        display_internal_msg("wrong_login", is_error=True)
    except Exception as e:
        logging.error(f"خطأ تسجيل دخول: {str(e)}")
        display_internal_msg("unexpected_error", is_error=True)

def trigger_error():
    hide_internal_msg()
    try:
        res = 10 / 0
    except Exception as ex:
        logging.error(f"خطأ نظام تجريبي: {str(ex)}")
        display_internal_msg("unexpected_error", is_error=True)

# ==========================================
# 5. بناء واجهة المستخدم الرسومية المستقرة
# ==========================================
init_db()

root = tk.Tk()
root.title("Security System Final")
root.geometry("450x780")
root.configure(bg="#f4f6f7")

# نصوص العناوين الثابتة في أندرويد تظهر بشكل طبيعي تلقائياً
tk.Label(root, text="نظام التأمين البرمجي المتكامل", font=("Arial", 16, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=15)

# الإطار الثابت والنهائي للرسائل الداخلية
embedded_msg_box = tk.Frame(root, bd=1, relief="solid", highlightthickness=1)
embedded_msg_label = tk.Label(embedded_msg_box, justify="center")
embedded_msg_label.pack(padx=10, pady=10)

# إطار الحقول والمدخلات التفاعلية
fields_frame = tk.Frame(root, bg="#f4f6f7")
fields_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(fields_frame, text="اسم المستخدم للتسجيل فقط", bg="#f4f6f7", font=("Arial", 11), fg="#34495e").pack(pady=2)
username_input = tk.Entry(fields_frame, width=30, justify='center', font=("Arial", 13), bd=2, relief="groove")
username_input.pack(pady=5)

tk.Label(fields_frame, text="البريد الإلكتروني", bg="#f4f6f7", font=("Arial", 11), fg="#34495e").pack(pady=2)
email_input = tk.Entry(fields_frame, width=30, justify='center', font=("Arial", 13), bd=2, relief="groove")
email_input.pack(pady=5)

tk.Label(fields_frame, text="كلمة المرور", bg="#f4f6f7", font=("Arial", 11), fg="#34495e").pack(pady=2)
password_input = tk.Entry(fields_frame, show="*", width=30, justify='center', font=("Arial", 13), bd=2, relief="groove")
password_input.pack(pady=5)

# أزرار التفاعل والمواجهة
tk.Button(fields_frame, text="إنشاء حساب آمن", bg="#27ae60", fg="white", width=25, font=("Arial", 12, "bold"), bd=1, relief="raised", command=register_process).pack(pady=15)
tk.Button(fields_frame, text="تسجيل دخول محمي", bg="#2980b9", fg="white", width=25, font=("Arial", 12, "bold"), bd=1, relief="raised", command=login_process).pack(pady=5)

# فاصل هيكلي ديكوري للواجهة
tk.Frame(fields_frame, height=2, bd=1, relief=tk.SUNKEN, bg="#bdc3c7").pack(fill=tk.X, padx=40, pady=15)

# قسم اختبار معالجة الأخطاء والـ Debugging الآمن
error_section_frame = tk.Frame(fields_frame, bg="#f4f6f7")
error_section_frame.pack(pady=5)
tk.Label(error_section_frame, text="قسم اختبار معالجة الأخطاء الآمنة", bg="#f4f6f7", font=("Arial", 11, "italic"), fg="#7f8c8d").pack()
tk.Button(error_section_frame, text="توليد خطأ نظام تجريبي", bg="#c0392b", fg="white", width=25, font=("Arial", 12, "bold"), bd=1, relief="raised", command=trigger_error).pack(pady=10)

root.mainloop()
