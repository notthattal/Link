# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Command to run your app (adjust if not Flask)
CMD ["python", "app.py"]