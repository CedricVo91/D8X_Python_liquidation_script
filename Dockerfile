FROM python:3.9-slim

# Set the working directory in the container
ENV LOG_DIR=/usr/src/app/logs
WORKDIR /usr/src/app

# Set the LOG_DIR environment variable
ENV LOG_DIR=/usr/src/app/logs

# Install tzdata for timezone support
RUN apt-get update

# Copy all files from the current directory into the working directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The command to run your Python script
CMD ["python", "src/liquidation/app.py"]