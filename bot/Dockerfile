FROM python:3.10-alpine
COPY . /bot
WORKDIR /bot
RUN mkdir -p logs
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps
CMD ["python", "bot.py"]
