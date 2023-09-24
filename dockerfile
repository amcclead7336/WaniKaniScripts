FROM python:3.10

WORKDIR /opt/WK_Review

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY wk_progress_review.py .
COPY app.py .
COPY assets ./assets/

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app:server"]