# Use official Python 3.11 image as the base
FROM python:3.11

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies without cache to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (your app code) into the container
COPY . .

# Expose port 8000 (default for gunicorn)
EXPOSE 8000

# Run gunicorn server to serve your Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
