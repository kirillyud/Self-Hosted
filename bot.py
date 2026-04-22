import telebot
import requests
import time
from telebot import types
import os
from dotenv import load_dotenv

load_dotenv()

bot_key = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(bot_key)

user_states = {}
user_data = {}

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
    button_add = types.InlineKeyboardButton('add', callback_data='add')
    markup.add(button_add)
    bot.send_message(message.chat.id, 'проекты', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add")
def handle_add(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_repo"
    bot.edit_message_text("ссылка на репозиторий", call.message.chat.id, call.message.message_id)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if user_states.get(user_id) == "waiting_repo":
        user_data[user_id] = {"repo": message.text}
        user_states[user_id] = "waiting_name"
        bot.send_message(message.chat.id, "название проекта")
        return

    if user_states.get(user_id) == "waiting_name":
        user_data[user_id]["name"] = message.text.strip()
        user_states[user_id] = "waiting_port"
        bot.send_message(message.chat.id, "порт")
        return

    if user_states.get(user_id) == "waiting_port":
        user_data[user_id]["port"] = message.text
        user_states[user_id] = "waiting_command"
        bot.send_message(message.chat.id, "команда запуска")
        return

    if user_states.get(user_id) == "waiting_command":
        user_data[user_id]["command"] = message.text
        data = user_data[user_id]
        text = (
            f"repo: {data['repo']}\n"
            f"name: {data['name']}\n"
            f"port: {data['port']}\n"
            f"command: {data['command']}"
        )
        markup = types.InlineKeyboardMarkup()
        button_ok = types.InlineKeyboardButton("OK", callback_data="confirm_add")
        markup.add(button_ok)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        user_states[user_id] = "confirm"
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith("project:"))
def handle_info(call):
    markup = types.InlineKeyboardMarkup()
    button_delete = types.InlineKeyboardButton('delete', callback_data=f'delete:{call.data.split(":")[1]}')
    button_deploy = types.InlineKeyboardButton('deploy',callback_data=f'deploy:{call.data.split(':')[1]}')
    button_stop = types.InlineKeyboardButton('stop',callback_data=f'stop:{call.data.split(':')[1]}')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{call.data.split(':')[1]}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    markup.add(button_deploy, button_stop, button_back, button_logs, button_delete)
    bot.edit_message_text(f'проект - {call.data.split(':')[1]}', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_add")
def confirm_add(call):
    user_id = call.from_user.id
    data = user_data[user_id]
    requests.post(
        "http://127.0.0.1:8000/projects",
        json={
            "name": data["name"].strip(),
            "repo_url": data["repo"],
            "command": data["command"],
            "port": data["port"]
        }
    )
    del user_states[user_id]
    del user_data[user_id]
    data = resp_json('http://127.0.0.1:8000/projects')
    markup = types.InlineKeyboardMarkup()
    for project in data:
        button = types.InlineKeyboardButton(
            f"{project['name']} - {project['status']}",
            callback_data=f"project:{project['name']}"
        )
        markup.add(button)
    button_add = types.InlineKeyboardButton('add', callback_data='add')
    markup.add(button_add)
    bot.edit_message_text(
        "проекты",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop:"))
def handle_stop(call):
    name = call.data.split(':')[1]
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy', callback_data=f'deploy:{name}')
    button_stop = types.InlineKeyboardButton('stop', callback_data=f'stop:{name}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{name}')
    markup.add(button_deploy, button_back, button_stop, button_logs)
    bot.edit_message_text("status - stopping", call.message.chat.id, call.message.message_id)
    requests.post(f'http://127.0.0.1:8000/stop/{name}')
    time.sleep(1)
    data = resp_json(f'http://127.0.0.1:8000/projects/{name}')
    bot.edit_message_text(
        f"name - {data['name']}\nstatus - {data['status']}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("deploy:"))
def handle_deploy(call):
    name = call.data.split(':')[1]
    markup = types.InlineKeyboardMarkup()
    button_deploy = types.InlineKeyboardButton('deploy', callback_data=f'deploy:{name}')
    button_stop = types.InlineKeyboardButton('stop', callback_data=f'stop:{name}')
    button_back = types.InlineKeyboardButton('back',callback_data=f'back:projects')
    button_logs = types.InlineKeyboardButton('logs',callback_data=f'logs:{name}')
    markup.add(button_deploy, button_back, button_stop, button_logs)
    name = call.data.split(':')[1]
    bot.edit_message_text("status - starting", call.message.chat.id, call.message.message_id)
    requests.post(f'http://127.0.0.1:8000/deploy/{name}')
    time.sleep(1)
    data = resp_json(f'http://127.0.0.1:8000/projects/{name}')
    bot.edit_message_text(
        f"name - {data['name']}\nstatus - {data['status']}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('back:'))
def back_to_projects(call):
    data = resp_json('http://127.0.0.1:8000/projects')
    markup = types.InlineKeyboardMarkup()
    for project in data:
        button_info = types.InlineKeyboardButton(f'{project['name']} - {project['status']}', callback_data=f'project:{project['name']}')
        markup.add(button_info)
    button_add = types.InlineKeyboardButton('add', callback_data='add')
    markup.add(button_add)
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


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
def handle_delete(call):
    name = call.data.split(":")[1].strip()
    requests.delete(f'http://127.0.0.1:8000/projects/{name}')
    data = resp_json('http://127.0.0.1:8000/projects')
    markup = types.InlineKeyboardMarkup()
    for project in data:
        button = types.InlineKeyboardButton(
            f"{project['name']} - {project['status']}", callback_data=f"project:{project['name']}")
        markup.add(button)
    button_add = types.InlineKeyboardButton('add', callback_data='add')
    markup.add(button_add)
    bot.edit_message_text("проекты", call.message.chat.id, call.message.message_id, reply_markup=markup)

if __name__ == '__main__':
    bot.polling(none_stop=True)