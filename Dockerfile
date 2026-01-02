# 1. Use a lightweight Python base image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application files
COPY . .

# 5. Expose the port Streamlit uses
EXPOSE 8501

# 6. Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]