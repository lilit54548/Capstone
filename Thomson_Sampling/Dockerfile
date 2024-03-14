# Use a base Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install any dependencies directly
# Add or replace with any other dependencies your application needs
RUN pip install --no-cache-dir numpy pandas

# Copy the content of the local src directory to the working directory
COPY . .

# Expose the port the service listens on
EXPOSE 5000

# Command to run the application
CMD ["python", "thompson_sampling.py"]

