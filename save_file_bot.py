import telebot
from telebot import types
from time import sleep
import json


with open("tokens.json", "r") as file:
    token = json.load(file)["save_file_bot"]


class State(object):
    __States = {0: 'commands', 1: 'main_menu', 2: 'save', 3: 'download', 4: 'search', 5: 'file_manager', 6: 'delete',
                7: 'delete_q', 8: 'rename', 9: 'edit', }

    @staticmethod
    def __throw_incorrect(x):
        if x not in State.__States:
            raise ValueError("State class: no state %i exists." % x)

    def __init__(self, x):
        State.__throw_incorrect(x)
        self.__state = x

    def set_state(self, x):
        State.__throw_incorrect(x)
        self.__state = x

    def get_state(self):
        return self.__state

    def get_str(self):
        return State.__States[self.__state]

    def __str__(self):
        return State.__States[self.__state]

    def __eq__(self, other):
        if type(other) == int:
            State.__throw_incorrect(other)
            return self.__state == other
        else:
            return self.__state == other.__state

    def __ne__(self, other):
        return not self == other


State.Commands = State(0)
State.MainMenu = State(1)
State.Save = State(2)
State.Download = State(3)
State.Search = State(4)
State.FileManager = State(5)
State.Delete = State(6)
State.DeleteQ = State(7)
State.Rename = State(8)
State.Edit = State(9)

bot = telebot.TeleBot(token)


def save():
    temp = open('data_base.txt', 'w', encoding='utf8')
    temp.write(f'file_system_data = {str(file_system_data)}\n'
               f'current_file = {str(current_file)}')
    temp.close()


file_system_data = {}
current_file = {}
for line in open("data_base.txt", "r", encoding="utf8").read().splitlines():
    exec(line)
users = [576109089, 1055941724, 5346695571]
file_system_default = {'main': ['', 'home', ], 'home': ['main', ]}
state = State(0)
message_worker_mode = True
m_w_file_system_mode = False


def find_new_name(name, user_id):
    current_name = 0
    while True:
        ans = f'{name}{" " + str(current_name) if current_name else ""}'
        if ans not in file_system_data[user_id]:
            return ans
        current_name += 1


def delete(file, user):
    if len(file_system_data[user][file]) > 1:
        for index, item in enumerate(file_system_data[user][file]):
            if index:
                delete(item, user)
    file_system_data[user][file_system_data[user][file][0]].remove(file)
    del file_system_data[user][file]
    save()


def help_me(message):
    if state == State.MainMenu:
        bot.send_message(message.from_user.id,
                         'Так, слушай и запоминай...\n'
                         '    Сохранить файл - сохраняет файл в облако.\n' +
                         '    Загрузить файл - позволяет выбрать и загрузить файл.\n' +
                         '    Искать файл - ищет файлы по введённым данным.\n'
                         '    "/help" - выводит подсказку.')
    if state == State.FileManager:
        bot.send_message(message.from_user.id,
                         'Так, слушай и запоминай...\n'
                         '    "back" - вернуться в предыдущую папку.\n'
                         '    "/start" - возвращает в главное меню.\n'
                         '    "delete" - удалит текущую папку.\n'
                         '    "rename" - переназвать текущую папку.\n'
                         '    "create" - создать новую папку в текущей.\n'
                         '    "add" - сохраняет файл в облако.\n')
    if state == State.Edit:
        bot.send_message(message.from_user.id,
                         'Так, слушай и запоминай...\n'
                         '    Введи имя для папки (только без повторов! я слежу...), чтобы завершить её создание.\n')
    if state == State.Delete:
        bot.send_message(message.from_user.id,
                         'Мне нечего сказать, пути назад нет... Хотя можешь попробовать "/start".')
    if state == State.DeleteQ:
        bot.send_message(message.from_user.id,
                         'Так, слушай и запоминай...\n'
                         '    Ответишь "Yes" - сотрёшь все данные в папке и её саму, '
                         '"No" - вернёшься в предудущее меню.')


def send_keyboard(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=1)
    if state == State.MainMenu:
        markup.add('Сохранить файл',
                   'Загрузить файл',
                   'Искать файл',
                   'Файловая система',
                   '/help')
        bot.send_message(user_id,
                         text='Привет, чем могу быть полезен?',
                         reply_markup=markup)
    elif state == State.FileManager:
        markup.row('back', '/start', '/help')
        if not file_system_data[user_id][current_file[user_id]][0]:
            markup.add('create')
        else:
            markup.row('delete', 'rename', 'create')
        for index, item in enumerate(file_system_data[user_id][current_file[user_id]]):
            if index:
                markup.add(item)
        bot.send_message(user_id,
                         text=f'Текущая папка:'
                              f' {current_file[user_id] if not current_file[user_id] == "main" else "Мой файловый менеджер"}',
                         reply_markup=markup)
    elif state == State.Edit:
        markup.row('/start', '/help')
        markup.add(find_new_name(name='new folder', user_id=user_id))
        bot.send_message(user_id,
                         text='Введи имя папки',
                         reply_markup=markup)
    elif state == State.DeleteQ:
        markup.row('/start', '/help')
        markup.add('Yes',
                   'No')
        bot.send_message(user_id,
                         text=f'Уверен? Это удалит все файлы и папки хранящиеся в {current_file[user_id]}.',
                         reply_markup=markup)
    elif state == State.Rename:
        markup.add('/start',
                   find_new_name(name='old folder', user_id=user_id))
        bot.send_message(user_id,
                         text=f'Как назовёшь папку "{current_file[user_id]}"?',
                         reply_markup=markup)


@bot.message_handler(commands=['start', 'help'])
def get_text_messages(message):
    global state
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(user_id, 'Вам отакзано в доступе.')
        print(f"\033[31m{message.from_user.username} access denied\n"
              f"\033[35m write\033[0m: \"{message.text}\"\n"
              f"\033[31mUser full\033[0m: {message.from_user}")
    else:
        print(f"\033[31m{message.from_user.username}\033[32m connected \n"
              f"\033[31mUser full\033[0m: {message.from_user}")

        if message.text == '/help':
            help_me(message)
            send_keyboard(message)
        elif message.text == '/start':
            state = State.MainMenu
            send_keyboard(message)
            if user_id not in file_system_data:
                file_system_data[user_id] = file_system_default
            if user_id not in current_file:
                current_file[user_id] = 'main'
    save()


@bot.message_handler(content_types=['text'])
def message_worker(message):
    global state
    global file_system_data
    global current_file
    user_id = message.from_user.id

    print(f'\033[31m{message.from_user.username}\033[35m write\033[0m: "{message.text}"\n'
          f'\033[31mUser full\033[0m: {message.from_user}')

    if user_id not in users:
        bot.send_message(user_id, 'Вам отказано в доступе.')
        print(f"\033[31m{message.from_user.username} access denied\n"
              f"\033[35m write\033[0m: \"{message.text}\"\n"
              f"\033[31mUser full\033[0m: {message.from_user}")
        return 0

    if state == State.MainMenu:
        if message.text == 'Загрузить файл':
            mode = False
            if mode:
                pass
            else:
                bot.send_message(user_id, 'Этого не умею, но может скоро научусь.')
        elif message.text == 'Сохранить файл':
            mode = False
            if mode:
                pass
            else:
                bot.send_message(user_id, 'Ой, я так не умею, спроси что-нибудь другое.')
        elif message.text == 'Искать файл':
            mode = False
            if mode:
                pass
            else:
                bot.send_message(user_id, 'Ой, этого я пока не умею.')
        elif message.text == 'Файловая система':
            mode = True
            if mode:
                state = State.FileManager
                send_keyboard(message)
            else:
                bot.send_message(user_id, 'А что это?')

    elif state == State.FileManager:
        if message.text == 'delete':
            if not current_file[user_id] == 'main':
                state = State.DeleteQ
                send_keyboard(message)
            else:
                bot.send_message(user_id, 'Нельзя удалять папку: "Мой файловый менеджер".')
        elif message.text == 'rename':
            if not current_file[user_id] == 'main':
                state = State.Rename
                send_keyboard(message)
            else:
                bot.send_message(user_id, 'Нельзя переименовывать папку: "Мой файловый менеджер".')
        elif message.text == 'create':
            state = State.Edit
            send_keyboard(message)
        elif message.text == 'back':
            if file_system_data[user_id][current_file[user_id]][0] != '':
                current_file[user_id] = file_system_data[user_id][current_file[user_id]][0]
                send_keyboard(message)
            else:
                bot.send_message(user_id, 'Ты и так уже в самомом начале')
        elif message.text in file_system_data[user_id]:
            current_file[user_id] = message.text
            send_keyboard(message)
        else:
            bot.send_message(user_id, 'Такого не знаю попробуй ещё раз')
            send_keyboard(message)

    elif state == State.Edit:
        if message.text not in file_system_data[user_id]:
            file_system_data[user_id][message.text] = [current_file[user_id], ]
            file_system_data[user_id][current_file[user_id]].append(message.text)
            current_file[user_id] = message.text
            bot.send_message(user_id, 'Новая папка создана.')
            state = State.FileManager
            send_keyboard(message)
            save()
        else:
            bot.send_message(user_id, f'Папка с именем "{message.text}" уже существует, попробуй другое.')

    elif state == State.DeleteQ:
        if message.text == 'Yes':
            temp = file_system_data[user_id][current_file[user_id]][0]
            delete(current_file[user_id], user_id)
            current_file[user_id] = temp
            bot.send_message(user_id, 'Папка была удалена')
        else:
            bot.send_message(user_id, 'Нет, так нет...')
        state = State.FileManager
        send_keyboard(message)

    elif state == State.Rename:
        new_name = message.text
        father = file_system_data[user_id][current_file[user_id]][0]
        if new_name not in file_system_data[user_id]:
            file_system_data[user_id][father].remove(current_file[user_id])
            file_system_data[user_id][father].append(new_name)
            for index, item in enumerate(file_system_data[user_id][current_file[user_id]]):
                if index:
                    file_system_data[user_id][item][0] = new_name
            file_system_data[user_id][new_name] = file_system_data[user_id].pop(current_file[user_id])
            bot.send_message(user_id, f'Папка "{current_file[user_id]}" была переименована в "{new_name}"')
            current_file[user_id] = new_name
            state = State.FileManager
            send_keyboard(message)
            save()
        else:
            bot.send_message(user_id, f'Папка с именем "{new_name}" уже существует, попробуй другое.')

    print(f'\033[31mState\033[0m: {state.get_str()}\n'
          f'\033[31mUser full\033[0m: {message.from_user}')
    save()


def polling():
    try:
        bot.polling(none_stop=True, interval=0)
    except BaseException as ex:
        print(type(ex).__name__, ex.args)
        sleep(1)
        polling()


polling()
