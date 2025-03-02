# Use official Python runtime as the base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements files first
COPY etc/base.txt etc/dev.txt etc/

# Install dependencies
RUN pip install --no-cache-dir -r etc/dev.txt

# Copy the entire microservice directory into the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the application using uvicorn server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
