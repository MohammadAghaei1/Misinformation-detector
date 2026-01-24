# استفاده از نسخه سبک پایتون
FROM python:3.10-slim

# تنظیم پوشه کاری
WORKDIR /app

# ۱. اول فقط فایل نیازمندی‌ها را کپی می‌کنیم
COPY requirements.txt .

# ۲. نصب کتابخانه‌ها (این لایه فقط وقتی requirements تغییر کند دوباره اجرا می‌شود)
RUN pip install --no-cache-dir -r requirements.txt

# ۳. حالا کل پروژه را کپی می‌کنیم (تغییرات کد شما در این مرحله اعمال می‌شود)
COPY . .

# اکسپوز کردن پورت‌ها
EXPOSE 8000
EXPOSE 8501

# اجرای همزمان بک‌اند و فرانت
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]