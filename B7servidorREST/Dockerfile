# Specify the parent image from which we build
FROM python:3.11
 
RUN mkdir -p /code

COPY . /code

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8001

# Run the application
ENTRYPOINT ["uvicorn", "app.main:app", "--host","0.0.0.0", "--port", "8001"]