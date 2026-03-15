FROM python:3.11

# Set working directory
WORKDIR /

# Make sure Python can import the "app" package
ENV PYTHONPATH=/

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app

# Expose port for HF Spaces
EXPOSE 7860

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]