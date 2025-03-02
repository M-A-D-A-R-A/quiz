FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first for better caching
COPY microservices/etc/base.txt .

# Install dependencies
RUN pip install --no-cache-dir -r base.txt

# Copy the rest of the application code
COPY microservices .

# Expose the port FastAPI runs on
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
