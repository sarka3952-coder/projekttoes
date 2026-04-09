FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Tento řádek zkopíruje vše, včetně složky templates:
COPY . . 
EXPOSE 8081
CMD ["python", "app.py"]
