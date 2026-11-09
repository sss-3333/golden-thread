FROM python:3.12-slim
RUN useradd --create-home app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app . .
USER app
CMD ["sh", "-c", "python app/extract.py && python app/verify.py && python app/load.py"]