FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m appuser
USER appuser
CMD ["python", "app.py"]