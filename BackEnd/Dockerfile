# Use a base Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install any dependencies directly
# Replace `fastapi` and `uvicorn` with any dependencies your application needs
RUN pip install --no-cache-dir fastapi uvicorn

# Copy the content of the local src directory to the working directory
COPY . .

# Expose the port the backend listens on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

