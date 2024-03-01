FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Copy requirements.txt to working directory
COPY requirements.txt /app/

# Install packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code to working directory
COPY . /app/

# Environment Variables
ENV ENV=production

# Run the main.py
CMD ["python", "-u", "main.py"]
