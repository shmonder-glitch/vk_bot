import bs4
import requests
import vk_api
import pymorphy2
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from weather import get_message


def get_keyboard(inline=False):
    keyboard = {
        "one_time": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"10\"}",
                    "label": "Погода на весь день"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"10\"}",
                    "label": "День"
                },
                "color": "primary"
            },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"10\"}",
                        "label": "Утро"
                    },
                    "color": "primary"
                }],
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"10\"}",
                    "label": "Вечер"
                },
                "color": "primary"
            },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"10\"}",
                        "label": "Ночь"
                    },
                    "color": "primary"
                }],
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"10\"}",
                    "label": "Погода в реальном времени"
                },
                "color": "secondary"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"10\"}",
                    "label": "Выбрать город"
                },
                "color": "negative"
            }]
        ],
        "inline": inline
    }
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def write_msg_with_forecast(user_id, city, time=25):
    vk.method('messages.send',
              {'user_id': user_id, 'message': get_message(city, time), 'random_id': vk_api.utils.get_random_id()})


def write_reminder(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message':
                                                               'Спасибо за использование данного бота :)&#10084;\n'
                                                               'Катя яя люблю тебяяяя11111111111111111',
              'random_id': vk_api.utils.get_random_id()})


def write_weather_buttons(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Выберите время или город &#128336;&#127751;',
                                'keyboard': get_keyboard(True),
                                'random_id': vk_api.utils.get_random_id()})


def write_incorrect_msg(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Несуществующая команда команда &#10060;\n'
                                                               '&#10071;&#10071;&#10071; Спешим напомнить вам, что получить список действий'
                                                               ' вы можете с помощью команды "погода" &#10071;&#10071;&#10071;\n',
                                'random_id': vk_api.utils.get_random_id(), 'keyboard': get_keyboard()})
    print('Error: Incorrect input')


def write_incorrect_city(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Некорректное название &#10060;  \n',
                                'random_id': vk_api.utils.get_random_id(), 'keyboard': get_keyboard()})


def write_correct_city(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Город успешно изменён &#9989;&#127961;',
                                'random_id': vk_api.utils.get_random_id()})


def write_city_choice(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Введите город или населённый пункт &#127747;',
                                'random_id': vk_api.utils.get_random_id()})


def write_info(user_id):
    vk.method('messages.send', {'user_id': user_id, 'message': 'Я бот погоды &#129302; \nПо умолчанию погода будет'
                                                               ' подбираться под '
                                                               'город, который указан у тебя в профиле &#127747; \nН'
                                                               'о его всегда можно изменить &#9989;&#9989;&#9989; \nНиже представлен'
                                                               ' список команд,'
                                                               ' которые ты можешь выполнить &#128172;\n'
                                                               '&#11015;&#11015;&#11015;&#11015;&#11015;&#11015;&#11015'
                                                               ';&#11015;&#11015;',
                                'random_id': vk_api.utils.get_random_id(), 'keyboard': get_keyboard()})



def output_code(code):
    print(f'Code: {code}')


TOKEN = "ba6713c40627ba9281241f8b6471c205ef2947306d20d44fe234454b5352d4aecdac76d24ef7a11bbf3c9"

vk = vk_api.VkApi(token=TOKEN)

longpoll = VkLongPoll(vk)

users = dict()

print("Server started")
city_choice = False

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:

            if event.user_id not in users:
                city = vk.method('users.get', {'user_id': event.user_id,
                                               'fields': ['city']})[0]
                
                if 'city' in city:
                    users[event.user_id] = city['city']['title']
                else:
                    users[event.user_id] = 'Санкт-Петербург'

            if city_choice:
                city_choice = False
                request = requests.get("https://sinoptik.com.ru/погода-" + event.text.lower())
                b = bs4.BeautifulSoup(request.text, "html.parser")
                r = b.select('.r404')
                if r:
                    output_code(-1)
                    write_incorrect_city(event.user_id)
                else:
                    users[event.user_id] = event.text.lower()
                    write_correct_city(event.user_id)
                    write_weather_buttons(event.user_id)
            elif event.text.lower() in ['начать', 'инфо']:
                write_info(event.user_id)
                write_weather_buttons(event.user_id)
            elif event.text.lower() == 'погода':
                write_weather_buttons(event.user_id)
                output_code(1)
            elif event.text.lower() == 'ночь':
                write_msg_with_forecast(event.user_id, users[event.user_id], 3)
                output_code(1)
                write_reminder(event.user_id)
            elif event.text.lower() == 'утро':
                write_msg_with_forecast(event.user_id, users[event.user_id], 9)
                output_code(1)
                write_reminder(event.user_id)
            elif event.text.lower() == 'день':
                write_msg_with_forecast(event.user_id, users[event.user_id], 15)
                output_code(1)
                write_reminder(event.user_id)
            elif event.text.lower() == 'вечер':
                write_msg_with_forecast(event.user_id, users[event.user_id], 21)
                output_code(1)
                write_reminder(event.user_id)
            elif event.text.lower() == 'погода на весь день':
                write_msg_with_forecast(event.user_id, users[event.user_id])
                output_code(1)
                write_reminder(event.user_id)
            elif event.text.lower() == 'выбрать город':
                write_city_choice(event.user_id)
                city_choice = True
            elif event.text.lower() == 'погода в реальном времени':
                write_msg_with_forecast(event.user_id, users[event.user_id], 26)
                output_code(1)
                write_reminder(event.user_id)
            else:
                output_code(0)
                write_incorrect_msg(event.user_id)
            '''elif True:
                city = vk.method('users.get', {'user_id': event.user_id, 'fields': ['city']})[0]['city']['title']
                write_msg(event.user_id, city)'''

            print('Text: ', event.text)
            print("-------------------")
