FROM python:3.8.15-buster
WORKDIR /app
COPY ["requirements.txt","/app/"]
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
RUN rm Dockerfile
CMD ["gunicorn"  , "--workers", "4" , "-b", "0.0.0.0:8000", "focus_back.wsgi:application"]