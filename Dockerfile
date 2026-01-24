# Use the official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# First, copy only the requirements file to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without caching the index to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose ports: 8000 for FastAPI backend and 8501 for Streamlit frontend
EXPOSE 8000
EXPOSE 8501

# Run both FastAPI and Streamlit simultaneously using a shell command
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]