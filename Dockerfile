FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port for Railway
EXPOSE $PORT

# Run the simplified bot (no event loop conflicts)
CMD ["python", "bot_simple.py"] 