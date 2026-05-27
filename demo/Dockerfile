# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install the requests library
RUN pip install --no-cache-dir requests

# Copy the demo script into the container
COPY demo/demo.py .

# Set the default command to run the script
CMD ["python", "demo.py"]