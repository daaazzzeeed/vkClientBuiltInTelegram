import vk
import telebot
import config
import json
import time

passw = config.vkPassw
login = config.vkLogin
appId = config.appId
myId = config.myId

vkAuthSession = vk.AuthSession(appId, login, passw, scope='wall, messages')
api = vk.API(vkAuthSession, v='5.69')


def parseJson(json_string, field1, field2):
    try:
        parsed_string = json.loads(json_string)
        substring = str(parsed_string[field1]).replace('[', '')
        substring = substring.replace(']', '')
        substring = substring.replace("'", '"')
        json_dict = json.loads(substring)
        return str(json_dict[field2])
    except (json.JSONDecodeError, TypeError):
        print('Error occurred')


def getFriends():
    resp3 = api.friends.get(user_id=myId, order='name', count='1000', offset='0', fields='name', name_case='nom')
    usersJsonList = resp3['items']
    config.count = 0
    for item in usersJsonList:
        name = str(item['first_name']) + ' ' + str(item['last_name'])
        user_id = str(item['id'])
        config.count += 1
        config.friends_dict.update({name: user_id})


def get_users(user_id):
    return api.users.get(user_ids=user_id)

getFriends()

bot = telebot.TeleBot(config.ApiToken)
print('бот запущен')


@bot.message_handler(commands=['get'])
def get_messages(msg):
    resp = api.messages.get(count='1')
    resp = str(resp).replace("'", '"')
    us_id = parseJson(resp, 'items', 'user_id')
    resp2 = get_users(us_id)
    resp2 = str(resp2).replace("'", '"')
    resp2 = resp2.replace('[', '')
    resp2 = resp2.replace(']', '')
    resp2 = json.loads(resp2)
    try:
        bot.send_message(msg.chat.id, 'Сообщение : ' + parseJson(resp, 'items', 'body') + ' от : ' + resp2['first_name'] + ' ' + resp2['last_name'])
    except TypeError:
        bot.send_message(msg.chat.id, '[Вложение]')


@bot.message_handler(commands=['quit'])
def finish(msg):
    bot.send_message(msg.chat.id, 'Бот завершил работу')
    quit(0)


@bot.message_handler(commands=['friends'])
def get_friends(msg):
    for item in config.friends_dict:
        bot.send_message(msg.chat.id, item)
    bot.send_message(msg.chat.id, 'Количество друзей : ' + str(config.count))


@bot.message_handler(commands=['send'])
def get_text(msg):
    send = bot.send_message(msg.chat.id, 'введите текст : ')
    bot.register_next_step_handler(send, get_name)


def get_name(msg):
    config.text = msg.text
    send = bot.send_message(msg.chat.id, 'введите имя : ')
    bot.register_next_step_handler(send, assure)


def assure(msg):
    config.name = msg.text
    bot.send_message(msg.chat.id, 'Сообщение ' + '[' + config.text + ']' + ' будет отправлено ' + '[' + config.name + ']')
    send = bot.send_message(msg.chat.id, 'Вы уверены? y/n')
    bot.register_next_step_handler(send, send_message)


def send_message(msg):
    user_response = msg.text
    if user_response == 'y':
        userId = config.friends_dict.get(config.name)
        api.messages.send(user_id=userId, message=config.text)
        bot.send_message(msg.chat.id, 'Отправлено')
    elif user_response == 'n':
        bot.send_message(msg.chat.id, 'Сообщение не будет отправлено')
while True:
    try:
        bot.polling(none_stop=True)
    except (KeyboardInterrupt, ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, json.JSONDecodeError, TypeError):
        print('Error occurred')
    time.sleep(1)
