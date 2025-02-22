# Use an official Python 3.10 image from Docker Hub
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the service account key file to the container
COPY keyfile.json /app/keyfile.json


# Define build arguments for sensitive information
ARG DB_PASSWORD
ARG DB_USERNAME
ARG MONGODB_URL
ARG MLFLOW_TRACKING_URI
ARG MLFLOW_TRACKING_USERNAME
ARG MLFLOW_TRACKING_PASSWORD

# Set environment variables using build arguments
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_USERNAME=$DB_USERNAME
ENV MONGODB_URL=$MONGODB_URL
ENV MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI
ENV MLFLOW_TRACKING_USERNAME=$MLFLOW_TRACKING_USERNAME
ENV MLFLOW_TRACKING_PASSWORD=$MLFLOW_TRACKING_PASSWORD




# Set environment variable for Google Cloud SDK authentication
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/keyfile.json

# Ensure the correct permissions for the key file
RUN chmod 644 /app/keyfile.json

# Copy the application code to the container
COPY . /app

# Install other dependencies for your application
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 5000

# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
