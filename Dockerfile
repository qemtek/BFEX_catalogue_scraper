FROM python:3.7.0

COPY . /betfair_exchange_data_engineering
WORKDIR /betfair_exchange_data_engineering
ADD main.py /

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]