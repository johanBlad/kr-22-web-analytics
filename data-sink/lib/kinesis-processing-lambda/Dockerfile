FROM public.ecr.aws/lambda/python:3.8

WORKDIR /app

COPY GeoLite2-City.mmdb .

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt

COPY  app.py  .

CMD ["/app/app.handler"]
