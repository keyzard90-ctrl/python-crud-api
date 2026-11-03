FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY app.py .
EXPOSE 5000
# Tugas D: Docker HEALTHCHECK (python:3.11-slim tidak punya curl, jadi pakai urllib)
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2).status == 200 else 1)"
CMD ["python", "app.py"]
