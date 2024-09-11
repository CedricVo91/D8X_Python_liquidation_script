FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install tzdata for timezone support
RUN apt-get update

# Copy all files from the current directory into the working directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The command to r un your Python script
CMD ["python", "src/liquidation/app.py"]