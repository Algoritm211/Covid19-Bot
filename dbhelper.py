from sqlalchemy import *
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, String, MetaData, Integer
import datetime

db_string = 'postgres://vvxriaqssfelql:de11e0d192212064b3b4e02a771b54dfb60d1dde6682131782d17c54ed607464@ec2-18-232-143-90.compute-1.amazonaws.com:5432/d3npm1gb6su6qo'

db = create_engine(db_string)

meta = MetaData(db)
USERS_TABLE = Table('users', meta,
                     Column('id', Integer, unique=True),
                     Column('name', String),
                     Column('linkuser', String),
                     Column('date', String),
                     Column('countries', String))


def write_user_to_db(id, name, linkuser, date):

    with db.connect() as conn:
        USERS_TABLE.create(checkfirst=True)
        insert_statement = insert(USERS_TABLE).values(id=id, name=name, linkuser=linkuser, date=date)
        do_nothing_statement = insert_statement.on_conflict_do_nothing(
                index_elements=['id']
        )
        conn.execute(do_nothing_statement)



def get_read():
    with db.connect() as conn:
        exp = USERS_TABLE.select()
        result = conn.execute(exp)
        for i in result:
            print(i)



def get_number_of_all_users():
    with db.connect() as conn:
        result = conn.execute(select([func.count(USERS_TABLE.c.id)]))
        return result.fetchone()[0]

def get_users_today(date):
    with db.connect() as conn:
        result = conn.execute(select([func.count(USERS_TABLE.c.id)]).where(USERS_TABLE.c.date == date))
        return result.fetchone()[0]


def get_users_month(month_date):
    with db.connect() as conn:
        month = '%' + month_date + '%'
        exp = select([func.count(USERS_TABLE.c.id)]).where(USERS_TABLE.c.date.like(month))
        result = conn.execute(exp)
        return result.fetchone()[0]


def get_users_year(year_date):
    with db.connect() as conn:
        year = '%' + year_date + '%'
        exp = select([func.count(USERS_TABLE.c.id)]).where(USERS_TABLE.c.date.like(year))
        result = conn.execute(exp)
        return result.fetchone()[0]

def get_info():
    now = datetime.datetime.now()
    current = now.strftime("%d-%m-%Y")
    day = now.strftime("%d")
    month = now.strftime("%m")
    year = now.strftime("%Y")
    all_users = str(get_number_of_all_users())
    users_day = str(get_users_today(current))
    users_month = str(get_users_month(month))
    users_year = str(get_users_year(year))
    text_message = '----------\n' + '📍<b>Актуальная информация о боте</b>📍\n' + '----------\n'
    text_message += '<i>В настоящий момент всего пользователей бота:</i> ' + all_users + '\n\n'
    text_message += '<i>Зарегистрировано сегодня:</i> '+ users_day + '\n\n'
    text_message += '<i>Зарегистрировано в этом месяце:</i> '+ users_month + '\n\n'
    text_message += '<i>Зарегистрировано в этом году:</i> '+ users_year + '\n\n'
    text_message += '<b>Информация предоставлена: </b> ' + '<b>' + current + '</b>'
    return text_message


def write_country_to_db(id, countries):

    with db.connect() as conn:
        insert_statement = insert(USERS_TABLE).values(id=id, countries=countries)
        do_update_statement = insert_statement.on_conflict_do_update(
            index_elements=['id'],
            set_=dict(countries=countries)
        )
        conn.execute(do_update_statement)

def get_user_country(message_id):
    with db.connect() as conn:
        try:
            result = conn.execute(select([USERS_TABLE.c.countries]).where(USERS_TABLE.c.id == message_id))
            return result.fetchone()[0]
        except:
            return None

def users_list():
    with db.connect() as conn:
        result = conn.execute(select([USERS_TABLE.c.id]))
        return [elem[0] for elem in result.fetchall()]

# print(users_list())
