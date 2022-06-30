FROM python:3.9
EXPOSE 8080
WORKDIR /ailegaladvisor
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
WORKDIR /ailegaladvisor/src
CMD streamlit run --server.port 8080 --server.enableCORS false app.py