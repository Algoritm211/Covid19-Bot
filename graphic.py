from sqlalchemy import *
import sqlalchemy
# from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, String, MetaData, Integer
import datetime
import matplotlib.pyplot as plt
from pylab import *
import random
import psycopg2
import os
import math
from datetime import datetime
from threading import Timer
from bs4 import BeautifulSoup
import urllib.request
import datetime
from urllib.request import urlopen, Request

db_string = 'postgres://vvxriaqssfelql:de11e0d192212064b3b4e02a771b54dfb60d1dde6682131782d17c54ed607464@ec2-18-232-143-90.compute-1.amazonaws.com:5432/d3npm1gb6su6qo'

db = create_engine(db_string)

meta = MetaData(db)
INFO_TABLE = Table('coronadata', meta, autoload=True)
active = []
death = []
recovered = []
date = []
with db.connect() as conn:
    result = conn.execute(INFO_TABLE.select().order_by('active'))
    for i in result.fetchall():
        active.append(i[0])
        death.append(i[1])
        recovered.append(i[2])
        date.append(i[3])

class Graphic:

    def __init__(self, active, death, recovered, date):
        self.active = active
        self.death = death
        self.recovered = recovered
        self.date = date


    def create_graphic(self):
        plt.figure(figsize=(8,5), dpi=100)
        plt.title('Coronavirus graphic in Ukraine from 20.03.2020')
        plt.xlabel('Date')
        plt.ylabel('Number of people')
        plt.plot(self.date, self.active, c='#DF013A', label='Active', linewidth=2)
        plt.plot(self.date, self.death, c='#000000', label='Death', linewidth=2)
        plt.plot(self.date, self.recovered, c='#008000', label='Recovered', linewidth=2)
        '''Интревал(каждая n строка показывается)'''
        '''сделать зависимость от длины ряда данных'''
        len_list = len(self.date)
        NUMBER_DATE = 5
        number_of_date = math.ceil(len_list/NUMBER_DATE)
        # date = self.date[::number_of_date]
        # date = [datetime.strptime(x, '%d-%m-%Y') for x in date]
        plt.xticks(self.date[::number_of_date])
        '''Поворот значений по оси х(для удобного представления)'''
        plt.xticks(rotation=4, horizontalalignment='center')
        plt.yticks(rotation=5, horizontalalignment='right')
        plt.legend()
        plt.savefig(figsize=(19.20, 18.80),fname='Coronagr.png', dpi=300)

# gr_btc = Graphic(Bitcoin, Date, 'Bitcoin', '#610B21', 'GRbtc.png', 1)
def get_graphic_ukr():
    gr = Graphic(active, death, recovered, date)
    gr.create_graphic()

def timed_job():

    Timer(43200, timed_job).start()
    with db.connect() as conn:
        now = datetime.datetime.now()
        date = now.strftime('%d-%m-%Y')
        headers = {'User-Agent': 'Safari/537.3'}
        reg_url = 'https://nv.ua/amp/koronavirus-v-ukraine-karta-novosti-ukrainy-50075556.html'
        req_1 = Request(url=reg_url, headers=headers)
        html = urlopen(req_1).read()
        soup = BeautifulSoup(html, 'lxml')
        indicators = []
        info = soup.find(name='div', attrs={'class':'subtitle'}).get_text().split()
        for elem in info:
            if elem.isdigit():
                indicators.append(elem)
        data = {
        'active': indicators[1] + indicators[2],
        'death': indicators[3],
        'recovered': indicators[4]
        }
        INFO_TABLE.create(checkfirst=True)
        insert_statement = sqlalchemy.dialects.postgresql.insert(INFO_TABLE).values(active=int(data['active']), death=int(data['death']), recovered=int(data['recovered']), date=date)
        do_nothing_statement = insert_statement.on_conflict_do_nothing(
                index_elements=['date']
        )
        conn.execute(do_nothing_statement)


timed_job()
