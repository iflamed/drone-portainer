FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY plugin.py plugin.sh ./

# ENTRYPOINT ["python", "/usr/src/app/plugin.py"]
ENTRYPOINT ["/usr/src/app/plugin.sh"]
