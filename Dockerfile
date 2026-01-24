FROM python:3.10-slim
WORKDIR /app

# ابتدا فقط لیست کتابخانه‌ها را کپی و نصب کن
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# حالا بقیه کدها را کپی کن. این کار باعث می‌شود اگر کد عوض شد، داکر لایه جدید بسازد
COPY . .

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]