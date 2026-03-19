import telebot
import requests
import time
from telebot import types
bot_key = '8738690991:AAES73Zwsk-pXSYUS9cb9lsOeFYWHTNhVEI'
bot = telebot.TeleBot(bot_key)

def resp_json(link):
    response = requests.get(link)
    return response.json()

def check_status(name):
    data = resp_json(f'http://127.0.0.1:8000/projects/{name}')
    return data['status']

@bot.message_handler(commands=['start'])
def handle_start(message):
    data = resp_json('http://127.0.0.1:8000/projects')
    markup = types.InlineKeyboardMarkup()
    for project in data:
        button = types.InlineKeyboardButton(f'{project['name']} - {project['status']}', callback_data=f'project:{project['name']}')
        markup.add(button)
    bot.send_message(message.chat.id, 'проекты', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("project:"))
def handle_info(call):
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy',callback_data=f'deploy:{call.data.split(':')[1]}')
    button_stop = types.InlineKeyboardButton('stop',callback_data=f'stop:{call.data.split(':')[1]}')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{call.data.split(':')[1]}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    markup.add(button_deploy, button_stop, button_back, button_logs)
    bot.edit_message_text(f'проект - {call.data.split(':')[1]}', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop:"))
def handle_stop(call):
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy', callback_data=f'deploy:{call.data.split(':')[1]}')
    button_stop = types.InlineKeyboardButton('stop', callback_data=f'stop:{call.data.split(':')[1]}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{call.data.split(':')[1]}')
    markup.add(button_deploy, button_back, button_stop, button_logs)
    bot.edit_message_text(f'status - stopping', call.message.chat.id, call.message.message_id)
    requests.post(f'http://127.0.0.1:8000/stop/{call.data.split(':')[1]}')
    for i in range(10):
        if check_status(call.data.split(':')[1]) == 'stopped':
            break
        else:
            time.sleep(0.3)
    data = resp_json(f'http://127.0.0.1:8000/projects/{call.data.split(':')[1]}')
    bot.edit_message_text(f'name - {data['name']}\nstatus - {data['status']}', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("deploy:"))
def handle_deploy(call):
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy', callback_data=f'deploy:{call.data.split(':')[1]}')
    button_stop = types.InlineKeyboardButton('stop', callback_data=f'stop:{call.data.split(':')[1]}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{call.data.split(':')[1]}')
    markup.add(button_deploy, button_back, button_stop, button_logs)
    bot.edit_message_text(f'status - starting', call.message.chat.id, call.message.message_id)
    requests.post(f'http://127.0.0.1:8000/deploy/{call.data.split(':')[1]}')
    for i in range(10):
        if check_status(call.data.split(':')[1]) == 'running':
            break
        else:
            time.sleep(0.3)
    data = resp_json(f'http://127.0.0.1:8000/projects/{call.data.split(':')[1]}')
    bot.edit_message_text(f'name - {data['name']}\nstatus - {data['status']}', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back:'))
def back_to_projects(call):
    data = resp_json('http://127.0.0.1:8000/projects')
    markup = types.InlineKeyboardMarkup()
    for project in data:
        button = types.InlineKeyboardButton(f'{project['name']} - {project['status']}', callback_data=f'project:{project['name']}')
        markup.add(button)
    bot.edit_message_text('проекты', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('logs:'))
def get_logs(call):
    markup = types.InlineKeyboardMarkup()
    data = resp_json(f'http://127.0.0.1:8000/projects/{call.data.split(':')[1]}/logs')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back_project:{call.data.split(':')[1]}')
    markup.add(button_back)
    bot.edit_message_text(data, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_project:'))
def back_to_project(call):
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy',callback_data=f'deploy:{call.data.split(':')[1]}')
    button_stop = types.InlineKeyboardButton('stop',callback_data=f'stop:{call.data.split(':')[1]}')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{call.data.split(':')[1]}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    markup.add(button_deploy, button_stop, button_back, button_logs)
    bot.edit_message_text(f'проект - {call.data.split(':')[1]}', call.message.chat.id, call.message.message_id, reply_markup=markup)

if __name__ == '__main__':
    bot.polling()