FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install tzdata for timezone support
RUN apt-get update && apt-get install -y tzdata

# Set timezone to Europe/Zurich (or another timezone if needed)
ENV TZ=Europe/Zurich
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy all files from the current directory into the working directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The command to run your Python script
CMD ["python", "./liquidate_positions_final.py"]