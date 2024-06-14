# Specify base image
FROM python:3.11.2  

EXPOSE 8080
ENV PORT 8080

RUN groupadd -g 900 appuser && \
    useradd -r -u 900 -g appuser appuser

WORKDIR /home

COPY . /home
RUN chown -R appuser:appuser /home

# Switch to appuser to avoid running as root user
USER appuser

RUN pip install -r /home/requirements.txt

CMD python3 /home/app.py