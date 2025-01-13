FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install pika pillow
CMD ["python", "image_resizer.py"]
