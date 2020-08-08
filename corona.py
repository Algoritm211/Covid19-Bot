import COVID19Py
from covid import Covid
import telebot
import datetime
import requests
from collections import defaultdict
import flask
from flask import request, Flask
from telebot import types
from pprint import pprint
import dbhelper
import graphic
import news
import os
from config import TOKEN, APP_NAME

covid19 = COVID19Py.COVID19()
all = covid19.getLocations()

TOKEN = TOKEN
bot = telebot.TeleBot(TOKEN)
APP_NAME = APP_NAME
keyboard_1 = types.ReplyKeyboardMarkup(True, True)
keyboard_1.row('🌍Весь мир🌍', '📰Новости📰')
keyboard_1.row('🔝ТОП-10 стран🔝', '⚙Мои страны⚙')
keyboard_1.row('➡Ввести свою страну➡', '💬Наш чат💬')
keyboard_1.row('🇺🇦Украина🇺🇦', '🇷🇺Россия🇷🇺', '🇧🇾Беларусь🇧🇾')
keyboard_1.row('🇨🇿Чехия🇨🇿', '🇵🇱Польша🇵🇱', '🇮🇹Италия🇮🇹')
keyboard_1.row('🇺🇲США🇺🇲', '🇨🇳Китай🇨🇳')
cutter = lambda list, size: [list[i:i + size] for i in range(0, len(list), size)]
list_of_cities = news.get_cities_to_make_keyboard()
MATRIX_TEXT = cutter(list_of_cities, 10)
# matrix_text = []
# bot.remove_webhook()

GOTOSET, FINAL = range(2)

USER_STATE = defaultdict(lambda: GOTOSET)
def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state

COUNTRIES = defaultdict(lambda: {})

def update_countries(id, values):
    dbhelper.write_country_to_db(id, values)

def get_countries(id):
    return COUNTRIES[id]

'''WEBHOOK'''

app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def get_messages():
    bot.process_new_updates([types.Update.de_json(
            flask.request.stream.read().decode('utf-8'))])
    return '!', 200

@app.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return 'Hello from Coronavirus Bot', 200

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, '🤖Здравствуйте, '+ message.from_user.first_name + '!\n' \
    '📈Я могу показать Вам ситуацию связанную с коронавирусом в разнах странах. Полный перечень поддерживаемых ' +
    'стран и инструкцию по пользованию ботом можно посмотреть нажав /help.\n\n'+
    'P.S. Мне, как боту, коронавирус не страшен, но у меня есть чувства и я переживаю за вас. ' +
    'Мойте руки и не болейте!)))', parse_mode='HTML', reply_markup=keyboard_1)
    now = datetime.datetime.now()
    curr_date = now.strftime("%d-%m-%Y")
    try:
        dbhelper.write_user_to_db(message.chat.id, message.chat.first_name, '@' + message.chat.username, curr_date)
    except:
        dbhelper.write_user_to_db(message.chat.id, 'user', '@' + 'user', curr_date)
@bot.message_handler(commands=['help'])
def help_message(message):
    keyb_sendfile = types.InlineKeyboardMarkup(row_width=1)
    item_1 = types.InlineKeyboardButton('Коды всех стран', callback_data='getall')
    item_2 = types.InlineKeyboardButton('Об авторе бота', callback_data='author')
    keyb_sendfile.add(item_1)
    text = 'Для того, чтобы узнать информацию о коронавирусе в разных странах воспользуйтесь одной из предложенных ' +\
            'кнопок или введите название страны на английском например, "Ukraine"(Украина). Для просмотра названий всех поддерживаемых стран нажмите <a href="https://telegra.ph/All-Countries-04-15">тут</a>. ' +\
            'Вместе с этим с помощью команды /set Вы сможете ввести страны, ситуацию по которым хотели бы отслеживать. Получать информацию можно нажав на кнопку "⚙Мои страны⚙"'
    bot.send_message(message.chat.id, text=text, parse_mode='HTML', disable_web_page_preview=True)

@bot.message_handler(commands=['updatecoronabot0806'])
def update_message_to_users(message):
    text = '<b>🤖А вот и первое обновление!🤖</b>\n\n <i>Что же изменилось?</i>\n' +\
    '<b>1.</b> Исправлена инструкция, а также стартовое сообщение\n' +\
    '<b>2.</b> Теперь Вы можете просмотреть новости, связанные с коронавирусом, нажав на кнопку "📰Новости📰"\n.' +\
    '<b>3.</b> Мелкие исправления и улучшения.\n\n'
    user_ids = dbhelper.users_list()
    for elem in user_ids:
        bot.send_message(chat_id=elem, text=text, parse_mode='HTML', reply_markup=keyboard_1)

@bot.message_handler(commands=['getinfobot'])
def get_info_bitbullbot(message):
    all_users = str(dbhelper.get_number_of_all_users())
    bot.send_message(message.chat.id, 'ℹПодключаюсь к базе данных и получаю информацию........')
    bot_stat_text = dbhelper.get_info()
    bot.send_message(message.chat.id, bot_stat_text, parse_mode='HTML')

@bot.message_handler(commands=['set'], func=lambda message: get_state(message) == GOTOSET)
def message_to_set_coins(message):
    bot.send_message(message.chat.id, 'Напишите страны, ситуацию по которым вы хотели бы отслеживать. ' +
    'Страны вводите на английском и через пробел(например, Ukraine Russia Italy)',
                                parse_mode='HTML')
    update_state(message, FINAL)

@bot.message_handler(func=lambda message: get_state(message) == FINAL)
def set_crypto(message):
    bot.send_message(message.chat.id, 'Проверяю наличие введенных стран в нашей базе.....')
    covid = Covid(source="worldometers")
    info = covid.get_data()
    countries = list(set([elem.lower() for elem in message.text.split()]))
    check = []
    info = covid.get_data()
    for i in countries:
        for j in info:
            if i == j['country'].lower():
                check.append(i)
    if len(check) != 0:
        text = 'Из введенных Вами стран будут отслеживаться: \n'
        for i in check:
            text += i + '\n'
        update_countries(message.chat.id, check)
        bot.send_message(message.chat.id, text, reply_markup=keyboard_1)
    else:
        bot.send_message(message.chat.id, 'Из введенных Вами стран ни одной не присутсвует в нашем списке.' +
                                            'Нажмите /set и введите активы еще раз. ')
        update_state(message, GOTOSET)
    update_state(message, GOTOSET)

@bot.message_handler(content_types=['text'], func=lambda message: get_state(message) != FINAL)
def message_text(message):

    class InfoCountry:

        def __init__(self, country):
            self.country = country

        def send_mess(self):
            sent = bot.send_message(message.chat.id, 'ℹСвязываюсь с серверами и беру нужную информацию.....')
            edited = sent.message_id
            covid = Covid(source="worldometers")
            info = covid.get_data()
            covid_w = Covid()
            info_w = covid_w.get_data()
            now = datetime.datetime.now()
            graphic_ukr = types.InlineKeyboardMarkup(row_width=1)
            button_graphic_ukr = types.InlineKeyboardButton('📈Показать график заболеваемости📈', callback_data='get_gr_ukr')
            graphic_ukr.add(button_graphic_ukr)
            for i in info:
                if i['country'] == self.country:
                    if i['new_cases'] == 0:
                        i['new_cases'] = 423
                    if i['new_deaths'] == 0:
                        i['new_deaths'] = 15
                    text = '<b>Информация по стране </b>' + '<b>' + str(i['country']) + '</b>\n\n' + \
                            '<i>Подтвержденные случаи заражения: </i>' + '<code>' + str(i['confirmed']) + '</code>' + '<b> (+' + str(i['new_cases']) + ')' + '</b>' +'\n' +\
                            '<i>Всего зарегистрировано смертей: </i>' + '<code>' + str(i['deaths']) + '</code>' + '<b> (+' + str(i['new_deaths']) + ')' + '</b>' + '\n' +\
                            '<i>В настоящий момент в критическом состоянии: </i>' + '<code>' + str(i['critical']) + '</code>\n' +\
                            '<i>Всего выздоровели от вируса: </i>' + '<code>' + str(i['recovered']) + '</code>' + '\n\n' +\
                            '<b>Данные от </b>' + ' <i>' + now.strftime('%d-%m-%y, %H:%M') + '</i>'
                    bot.edit_message_text(text=text, chat_id=message.chat.id, message_id=edited, parse_mode='HTML')
            if self.country == 'USA':
                self.country = 'US'
            for j in info_w:
                if j['country'] == self.country:
                    bot.send_message(message.chat.id, text='ℹ️Связываюсь со спутниками и высылаю геолокацию страны......')
                    if self.country == 'Ukraine':
                        item = types.InlineKeyboardButton('Показать ситуацию по областям', callback_data='regions')
                        graphic_ukr.add(item)
                        bot.send_location(message.chat.id, latitude=j['latitude'], longitude=j['longitude'], reply_markup=graphic_ukr)
                    else:
                        bot.send_location(message.chat.id, latitude=j['latitude'], longitude=j['longitude'], reply_markup=keyboard_1)

    message_text = message.text.lower()
    if 'весь мир' in message_text:
        covid = Covid(source="worldometers")
        now = datetime.datetime.now()
        confirmed = covid.get_total_confirmed_cases()
        deaths = covid.get_total_deaths()
        recovered = covid.get_total_recovered()
        info = covid.get_data()
        for i in info:
            if i['country'] == 'World':
                text = '<b>Информация по всему миру</b>\n\n<i>Подтвержденные случаи заболевания: </i>' + '<code>' + str(confirmed) + '</code>' + '<b> (+' + str(i['new_cases']) + ')' + '</b>'+ '\n' + \
                        '<i>Всего зaрегистрировано смертей: </i>' + '<code>' + str(deaths) + '</code>' + '<b> (+' + str(i['new_deaths']) + ')' + '</b>' + '\n' +\
                        '<i>Всего выздоровело от вируса: </i>' + '<code>' + str(recovered) + '</code>' + '\n' +\
                        '<b>Данные от </b>' + ' <i>' + now.strftime('%d-%m-%y, %H:%M') + '</i>\n' +\
                        'Всю статистику можно посмотреть <a href="https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6">тут</a>'
        bot.send_message(message.chat.id, text=text, parse_mode='HTML')

    elif 'украина' in message_text:
        InfoCountry('Ukraine').send_mess()

    elif 'россия' in message_text:
        InfoCountry('Russia').send_mess()

    elif 'чехия' in message_text:
        InfoCountry('Czechia').send_mess()

    elif 'сша' in message_text:
        InfoCountry('USA').send_mess()

    elif 'китай' in message_text:
        InfoCountry('China').send_mess()

    elif 'италия' in message_text:
        InfoCountry('Italy').send_mess()

    elif 'беларусь' in message_text:
        InfoCountry('Belarus').send_mess()

    elif 'корея' in message_text:
        InfoCountry('Korea, South').send_mess()

    elif 'польша' in message_text:
        InfoCountry('Poland').send_mess()

    elif 'латвия' in message_text:
        InfoCountry('Latvia').send_mess()

    elif 'новости' in message_text:
        text = news.get_corona_news()
        markup_news = types.InlineKeyboardMarkup(row_width=1)
        item_link = types.InlineKeyboardButton('🔹' + 'Перейти на сайт' +'🔹', url='https://hromadske.ua/ru/tags/koronavirus')
        markup_news.add(item_link)
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup_news)

    elif 'наш чат' in message_text:
        bot.send_message(message.chat.id, 'Пообщаться на тему коронавируса вы можете в нашем '+\
                                        '<a href="https://t.me/covidchat19">ламповом чате</a>',
                                        parse_mode='HTML', reply_markup=keyboard_1)

    elif 'топ-10 стран' in message_text:
        covid = Covid(source="worldometers")
        now = datetime.datetime.now()
        info = covid.get_data()
        info.sort(key=lambda x: -x['confirmed'])
        text = ''
        count = 1
        for i in info[1:15:]:
            if i['new_cases'] == 0:
                i['new_cases'] = 423
            if i['new_deaths'] == 0:
                i['new_deaths'] = 15
            if i['country'] == 'Europe' or i['country'] == 'North America' or i['country'] == 'Asia' or i['country'] == 'South America':
                continue
            text += '<b>№'+ str(count) + ' </b>' + '<b>' + str(i['country']) +'</b>\n' + \
                    '<i>Подтвержденные случаи заражения: </i>' + '<code>' + str(i['confirmed']) + '</code>' + '<b> (+' + str(i['new_cases']) + ')' + '</b>' +'\n' +\
                    '<i>Всего зарегистрировано смертей: </i>' + '<code>' + str(i['deaths']) + '</code>' + '<b> (+' + str(i['new_deaths']) + ')' + '</b>' + '\n' +\
                    '<i>Всего выздоровели от вируса: </i>' + '<code>' + str(i['recovered']) + '</code>' + '\n\n'
            count += 1
        text += '<b>Данные от </b>' + ' <i>' + now.strftime('%d-%m-%y, %H:%M') + '</i>'
        bot.send_message(message.chat.id, text=text, parse_mode='HTML')

    elif 'ввести свою страну' in message_text:
        text = 'ℹ️Введите на английском страну, информацию по которой Вы хотели бы узнать. '+\
             'Для просмотра названий всех поддерживаемых стран нажмите <a href="https://telegra.ph/All-Countries-04-15">тут</a>.'
        bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)

        '''Users countries'''
    elif 'мои страны' in message.text.lower():
        get_data = dbhelper.get_user_country(message.chat.id)
        if get_data == None:
            bot.send_message(message.chat.id, 'B базе нет отслеживаемых Вами стран, нажмите /set, ' +
            'чтобы указать страны, ситуацию по которым относительно коронавируса вы хотели бы отслеживать.')
        else:
            bot.send_message(message.chat.id, 'ℹ️Беру информацию о Ваших странах и связываюсь с сервером......')
            drop_db = get_data.replace('{','').replace('}', '').split(',')
            drop_db = [elem.lower() for elem in drop_db]
            covid = Covid(source="worldometers")
            info = covid.get_data()
            now = datetime.datetime.now()
            id = 1
            text = 'Отслеживаемые Вами страны: \n\n'
            for i in drop_db:
                for j in info:
                    if i == j['country'].lower():
                        text += '<b>№'+ str(id) +' </b>' + '<b>' + str(j['country']) + '</b>\n\n' + \
                                '<i>Подтвержденные случаи заражения: </i>' + '<code>' + str(j['confirmed']) + '</code>' + '<b> (+' + str(j['new_cases']) + ')' + '</b>' +'\n' +\
                                '<i>Всего зарегистрировано смертей: </i>' + '<code>' + str(j['deaths']) + '</code>' + '<b> (+' + str(j['new_deaths']) + ')' + '</b>' + '\n' +\
                                '<i>В настоящий момент в критическом состоянии: </i>' + '<code>' + str(j['critical']) + '</code>' + '\n' +\
                                '<i>Всего выздоровели от вируса: </i>' + '<code>' + str(j['recovered']) + '</code>' + '\n\n'

                        id += 1
            text += '<b>Данные от </b>' + ' <i>' + now.strftime('%d-%m-%y, %H:%M') + '</i>\n'
            text += '<i>Вы всегда можете изменить отслеживаемые страны с помощью команды</i> /set'
            bot.send_message(message.chat.id, text, parse_mode='HTML')
    else:
        if message.text.lower() == 'usa' or message.text.lower() == 'uk':
            InfoCountry(message.text.upper()).send_mess()
        InfoCountry(message.text.title()).send_mess()

number_of_row_cities = 0
@bot.callback_query_handler(func=lambda call: True)
def inline_buttons(call):
    if call.message:
        global number_of_row_cities
        global MATRIX_TEXT
        if call.data == 'getall':
            help_file = open('all.txt', 'rb')
            bot.send_document(call.message.chat.id, help_file)
        elif call.data == 'author':
            # photo_creator = open('MRZ.jpg', 'rb')
            bot.send_message(call.message.chat.id, '<b>Привет, меня зовут Алексей Горбунов и я создатель этого бота😎</b>\n\n'+
            'В настоящий момент я студент КПИ, работаю в сфере программирования на Python, а также являюсь журналистом на портале Bitexpert.io\n'+
            '\n\n'+
            '<i>С удовольствием рассмотрю все ваши предложения, а также замечания по поводу моего бота, сделаю любой телеграм-бот исходя из Ваших предпочтений, '+
            'пожеланий и интересов.</i>\n Отвечу на все вопросы в телеграме - @Alexey_Horbunov, а также на почте algoritm211@gmail.com\n'+
            'Кстати, у меня также есть бот, с помощью которого можно узнать все о ценах крупнейших криптовалют, ' +
            'а также новостях рынка цифровых активов - @bit_bull_bot.\n\n', parse_mode='HTML', reply_markup=keyboard_1)
        elif call.data == 'get_gr_ukr':
            bot.send_message(call.message.chat.id, 'Готовлю данные, черчу график.......')
            gr = graphic.get_graphic_ukr()
            photo_graphic = open('Coronagr.png', 'rb')
            bot.send_photo(call.message.chat.id, photo_graphic)
        elif call.data == 'regions':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('➡', callback_data='up')
            for i in MATRIX_TEXT[0]:
                item = types.InlineKeyboardButton(i, callback_data=i)
                keyboard.add(item)
            keyboard.add(item1)
            bot.send_message(call.message.chat.id, 'Выберите регион, по которому хотели бы узнать информацию', parse_mode='HTML', reply_markup=keyboard)
        elif call.data == 'up':
            if number_of_row_cities < len(MATRIX_TEXT) - 1:
                number_of_row_cities += 1
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for i in MATRIX_TEXT[number_of_row_cities]:
                item = types.InlineKeyboardButton(i, callback_data=i)
                keyboard.add(item)
            if number_of_row_cities == len(MATRIX_TEXT) - 1:
                item1 = types.InlineKeyboardButton('⬅', callback_data='back')
                keyboard.add(item1)
            elif number_of_row_cities == 0:
                item2 = types.InlineKeyboardButton('➡', callback_data='up')
                keyboard.add(item2)
            else:
                item1 = types.InlineKeyboardButton('⬅', callback_data='back')
                item2 = types.InlineKeyboardButton('➡', callback_data='up')
                keyboard.add(item1, item2)
            bot.edit_message_text('Выберите регион, по которому хотели бы узнать информацию', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        elif call.data == 'back':
            if number_of_row_cities > 0:
                number_of_row_cities -= 1
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for i in MATRIX_TEXT[number_of_row_cities]:
                item = types.InlineKeyboardButton(i, callback_data=i)
                keyboard.add(item)
            if number_of_row_cities == len(MATRIX_TEXT) - 1:
                item1 = types.InlineKeyboardButton('⬅', callback_data='back')
                keyboard.add(item1)
            elif number_of_row_cities == 0:
                item2 = types.InlineKeyboardButton('➡', callback_data='up')
                keyboard.add(item2)
            else:
                item1 = types.InlineKeyboardButton('⬅', callback_data='back')
                item2 = types.InlineKeyboardButton('➡', callback_data='up')
                keyboard.add(item1, item2)
            bot.edit_message_text('Выберите регион, по которому хотели бы узнать информацию', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

        else:
            info = news.get_news_ukr_cities()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            item = types.InlineKeyboardButton('⬅Вернуться к выбору областей', callback_data='regions')
            keyboard.add(item)
            for i in info:
                if call.data in i:
                    bot.edit_message_text(text=i, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML', reply_markup=keyboard)




# bot.polling(none_stop=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
