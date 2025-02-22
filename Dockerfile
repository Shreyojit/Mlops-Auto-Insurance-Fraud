# Use an official Python 3.10 image from Docker Hub
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the service account key file to the container
COPY credentials.json /app/credentials.json

# Set environment variable for Google Cloud SDK authentication
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Ensure the correct permissions for the key file
RUN chmod 644 /app/credentials.json

# Copy the application code to the container
COPY . /app

# Install other dependencies for your application
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 5000

# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
