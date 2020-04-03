FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install bs4
RUN pip install matplotlib
RUN pip install requests
RUN pip install lxml
RUN pip install flask
EXPOSE 5000
CMD ["python", "application.py"]