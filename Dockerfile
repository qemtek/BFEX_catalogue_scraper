FROM python:3.6

RUN apt-get -y update

# set a directory for the app
ADD . /betfair_exchange
WORKDIR /betfair_exchange

# copy all the files to the container
COPY . .
# install py libraries
RUN pip install -r requirements.txt

CMD python main.py $EVENT_TYPE_IDS $COUNTRY_CODES $MARKET_TYPES $MARKET_PROJECTION
