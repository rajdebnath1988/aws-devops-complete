FROM python:3.14.3-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Snyk/Trivy will scan this layer
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
