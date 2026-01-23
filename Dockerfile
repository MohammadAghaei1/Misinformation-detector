# Use the base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install the project dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports 8000 for FastAPI and 8501 for Streamlit
EXPOSE 8000
EXPOSE 8501

# Command to run both FastAPI and Streamlit using JSON array format
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py"]
