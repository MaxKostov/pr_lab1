FROM python:3.11-slim
WORKDIR /app
COPY server.py /app/server.py
COPY site /srv
EXPOSE 8000
ENTRYPOINT ["python","/app/server.py"]
CMD ["8000","/srv"]
