# Use a Python base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the application port
EXPOSE 3111

# Initialize the database with predefined posts
RUN python init_db.py

# Command to run the application
CMD ["python", "app.py"]