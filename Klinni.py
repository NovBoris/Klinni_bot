import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_req
from add_class import OrderClass, UserRequest, Admin
import time
import calendar
from math import ceil, floor
from google_sheets import gs_update
from db import db_update
import sqlite3

bot = telebot.TeleBot('5502235861:AAHzqGs8cakisXDVOA4TnC87yIIh7xfPiIo')
admin_group_id = -884604288
reviews_group_id = -850436301
user_id = {}
with sqlite3.connect('klinni_base.db') as con:
    cur = con.cursor()
    cur.execute("SELECT * FROM additional")
    additional = [list(filter(lambda x: x != '', i[1:])) for i in cur.fetchall()]
    cur.execute("SELECT chat_id FROM user_id WHERE access=1")
    admin_id = [int(i[0]) for i in cur.fetchall()]
    cur.execute("SELECT * FROM klinni_inf")
    klinni_inf = list(cur.fetchall()[0])
promo_code = {'123': 15, '1234': 20}
order = 1
order_req = 1


def fs(st):
    return st[0]


def dt(s):
    s = s[1:]
    return s


def text_res(call, user_id, promo=None):
    if promo is None:
        text = f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n' \
               f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'\
               f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'\
               f'Цена: {user_id[call.message.chat.id].price}р\n'\
               f'Дата: {user_id[call.message.chat.id].the_date}\n'\
               f'Время: {user_id[call.message.chat.id].time}\n'\
               f'ФИО: {user_id[call.message.chat.id].full_name}\n'\
               f'Адрес: {user_id[call.message.chat.id].address}\n'\
               f'Телефон: {user_id[call.message.chat.id].telephone}\n'\
               f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'\
               f'К оплате: {ceil(user_id[call.message.chat.id].total)}'
    else:
        text = f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'\
               f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'\
               f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'\
               f'Цена: {user_id[call.message.chat.id].price}р\n'\
               f'Дата: {user_id[call.message.chat.id].the_date}\n'\
               f'Время: {user_id[call.message.chat.id].time}\n'\
               f'ФИО: {user_id[call.message.chat.id].full_name}\n'\
               f'Адрес: {user_id[call.message.chat.id].address}\n'\
               f'Телефон: {user_id[call.message.chat.id].telephone}\n'\
               f'Почта : {user_id[call.message.chat.id].email}'\
               f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'\
               f'Сумма скидки за промокод: {floor((float(user_id[call.message.chat.id].total) / 100) * user_id[call.message.chat.id].promo_code[1])}р\n'\
               f'К оплате: {ceil(user_id[call.message.chat.id].total)}р'
    return text


def menu(call, user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Калькулятор', callback_data='0' + 'Калькулятор'),
                 InlineKeyboardButton('Описание услуг', callback_data='1' + 'Описание услуг'),
                 InlineKeyboardButton('Отзывы', callback_data='0' + 'Отзывы'))
    if user_id in admin_id:
        keyboard.row(InlineKeyboardButton('Административная панель', callback_data='0' + 'Административная'))
    keyboard.row(InlineKeyboardButton('Сообщение администратору', callback_data='0' + 'Сообщение'),
                 InlineKeyboardButton('Наш сайт', url='http://cleanny.by/'))
    try:
        bot.send_message(call.chat.id, 'КлинниБогини\nУборка квартир и домов в Минске и районе хорошо или бесплатно',
                         reply_markup=keyboard)
    except AttributeError:
        try:
            bot.edit_message_text('КлинниБогини\nУборка квартир и домов в Минске и районе хорошо или бесплатно',
                                  call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        except telebot.apihelper.ApiTelegramException:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             'КлинниБогини\nУборка квартир и домов в Минске и районе хорошо или бесплатно',
                             reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def message_handler(message):
    menu(message, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    global order
    global order_req
    global additional
    global admin_id
    flag = fs(call.data)
    data = dt(call.data)
    try:
        if data == 'Отзывы':
            def reviews(message):
                if message.text == '/start':
                    menu(message, message.chat.id)
                    return
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton('Опубликовать', callback_data='1' + 'Публикация отзыва'),
                             InlineKeyboardButton('Удалить', callback_data='2' + 'Удаление'))
                bot.send_message(admin_group_id,
                                 'От пользователя:  ' + '@' + message.from_user.username + '\nОтзыв:\n' + message.text,
                                 reply_markup=keyboard)
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
                bot.send_message(call.message.chat.id, 'Спасибо за ваш отзыв!', reply_markup=keyboard)

            review = bot.edit_message_text('Напишите свой отзыв', call.message.chat.id, call.message.message_id)
            bot.register_next_step_handler(review, reviews)
        elif data == 'Сообщение':
            def message_to_administrator(message):
                if message.text == '/start':
                    menu(message, message.chat.id)
                    return
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton('Рассмотрено', callback_data='1' + 'Рассмотрено'),
                             InlineKeyboardButton('Удалить', callback_data='2' + 'Удаление'))
                bot.send_message(admin_group_id,
                                 'От пользователя:  ' + '@' + message.from_user.username + '\nСообщение:\n' + message.text,
                                 reply_markup=keyboard)
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
                bot.send_message(call.message.chat.id, f'Вам ответят в ближайшее время\nвы можете позвонить нам'
                                                       f' и мы ответим на все вопросы\n+375(44)711-11-85',
                                 reply_markup=keyboard)
            review = bot.edit_message_text('Напишите свой вопрос, его рассмотрят в ближайшее время', call.message.chat.id,
                                           call.message.message_id)
            bot.register_next_step_handler(review, message_to_administrator)
        elif data == 'Публикация отзыва':
            bot.edit_message_text(chat_id=admin_group_id, message_id=call.message.message_id,
                                  text='Принято\n' + call.message.text)
            bot.send_message(reviews_group_id, call.message.text)
        elif data == 'Рассмотрено':
            bot.edit_message_text(chat_id=admin_group_id, message_id=call.message.message_id,
                                  text='Рассмотрено\n' + call.message.text)
        elif data == 'Удаление':
            bot.delete_message(call.message.chat.id, call.message.message_id)
        elif data == 'Меню':
            menu(call, call.message.chat.id)
        elif data == 'Административная':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Обновить GS', callback_data='1' + 'Обновить GS'),
                         InlineKeyboardButton('Обновить БД ', callback_data='1' + 'Обновить БД'),
                         InlineKeyboardButton('Статистика', callback_data='1' + 'Статистика'))
            keyboard.row(InlineKeyboardButton('Администраторы', callback_data='1' + 'Админы'),
                         InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            bot.edit_message_text('Панель администратора', call.message.chat.id, call.message.message_id,
                                  reply_markup=keyboard)
        elif data == 'Обновить GS':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            gs_message_id = bot.send_message(call.message.chat.id, 'Обновляюсь').message_id
            gs_update()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Обновить БД', callback_data='1Обновить БД'),
                         InlineKeyboardButton('Назад', callback_data='1Административная'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=gs_message_id, text='Обновление GS завершено\nХотите обновить бд?', reply_markup=keyboard)
        elif data == 'Обновить БД':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            gs_message_id = bot.send_message(call.message.chat.id, 'Обновляюсь').message_id
            db_update()
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM additional")
                additional = cur.fetchall()
            keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data='1Административная'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=gs_message_id, text='Обновление Базы данных завершено', reply_markup=keyboard)
            return additional
        elif data == 'Админы':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Добавить администратора', callback_data='1' + 'Добавить админ'),
                         InlineKeyboardButton('Убрать администратора', callback_data='1Убрать админ'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Административная'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Что хотите сделать', reply_markup=keyboard)
        elif data == 'Добавить админ':
            if flag == '1':
                user_id[call.message.chat.id] = Admin()

                def add_administrator_name(message):
                    try:
                        if message.text == '/start':
                            menu(message, message.chat.id)
                            return
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                        user_id[call.message.chat.id].name = message.text
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Повторить', callback_data='1' 'Добавить админ'),
                                     InlineKeyboardButton('Дальше', callback_data='2' + 'Добавить админ'))
                        keyboard.add(
                            InlineKeyboardButton('Назад', callback_data='1' 'Админы'))
                        bot.send_message(call.message.chat.id, 'Все верно?\n' + 'ФИО: ' + message.text, reply_markup=keyboard)
                    except KeyError:
                        menu(message, message.chat.id)
                administrator_name = bot.edit_message_text(text='Введите ФИО нового пользователя', chat_id=call.message.chat.id, message_id=call.message.message_id)
                bot.register_next_step_handler(administrator_name, add_administrator_name)
            if flag == '2':
                def add_administrator_id(message):
                    try:
                        if message.text == '/start':
                            menu(message, message.chat.id)
                            return
                        bot.delete_message(call.message.chat.id, call.message.message_id)
                        user_id[call.message.chat.id].id = message.text
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Повторить', callback_data='2' 'Добавить админ'),
                                     InlineKeyboardButton('Дальше', callback_data='3' + 'Добавить админ'))
                        keyboard.add(
                            InlineKeyboardButton('Назад', callback_data='1' 'Добавить админ'))
                        bot.send_message(call.message.chat.id, 'Все верно?\n' + 'id: ' + message.text, reply_markup=keyboard)
                    except KeyError:
                        menu(message, message.chat.id)
                administrator_id = bot.edit_message_text(text='Введите id нового пользователя', chat_id=call.message.chat.id,
                                               message_id=call.message.message_id)
                bot.register_next_step_handler(administrator_id, add_administrator_id)
            if flag == '3':
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton('Добавить', callback_data='4' + 'Добавить админ'),
                             InlineKeyboardButton('Отмена', callback_data='1' + 'Админы'))
                keyboard.add(InlineKeyboardButton('Назад', callback_data='2' + 'Добавить админ'))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f'Все верно?\n'
                                           f'ФИО: {user_id[call.message.chat.id].name}\n'
                                           f'id: {user_id[call.message.chat.id].id}', reply_markup=keyboard)
            if flag == '4':
                with sqlite3.connect('klinni_base.db') as con:
                    cur = con.cursor()
                    cur.execute("SELECT access FROM user_id WHERE chat_id=?", (int(user_id[call.message.chat.id].id), ))
                    res = cur.fetchone()
                    if len(res) == 0:
                        cur.execute("INSERT INTO user_id(chat_id, full_name) VALUES (?, ?)", (int(user_id[call.message.chat.id].id), user_id[call.message.chat.id].name))
                    else:
                        cur.execute("UPDATE user_id SET access = 1, chat_id=?, full_name=? WHERE chat_id=?", (int(user_id[call.message.chat.id].id), user_id[call.message.chat.id].name, int(user_id[call.message.chat.id].id)))
                cur.execute("SELECT chat_id FROM user_id WHERE access=1")
                admin_id = [int(i[0]) for i in cur.fetchall()]
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton('Меню', callback_data='2' + 'Админы'))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f'Пользователь добавлен', reply_markup=keyboard)
                return admin_id
        elif data == 'Убрать админ' or data.split(' :')[0] == 'Убрать админ':
            if flag == '1':
                with sqlite3.connect('klinni_base.db') as con:
                    cur = con.cursor()
                    cur.execute("SELECT full_name, chat_id FROM user_id WHERE access=1")
                    res = [list(i) for i in cur.fetchall()]
                    keyboard = InlineKeyboardMarkup()
                    for i in range(0, len(res) + 1, 2):
                        try:
                            keyboard.add(InlineKeyboardButton(res[i][0] + ' :' + str(res[i][1]), callback_data='2' + 'Убрать админ :' + str(res[i][1])))
                            keyboard.add(InlineKeyboardButton(res[i + 1][0] + ' :' + str(res[i + 1][1]), callback_data='2' + 'Убрать админ :' + str(res[i + 1][1])))
                        except IndexError:
                            break
                    keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Админы'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Кого удалить?', reply_markup=keyboard)
            if flag == '2':
                with sqlite3.connect('klinni_base.db') as con:
                    cur = con.cursor()
                    cur.execute("UPDATE user_id SET access=0 WHERE chat_id=?", (int(data.split(' :')[1]), ))
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Убрать админ'))
                    cur.execute("SELECT chat_id FROM user_id WHERE access=1")
                    admin_id = [int(i[0]) for i in cur.fetchall()]
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Пользователь удален', reply_markup=keyboard)
                    return admin_id
        elif data == 'Описание услуг':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT general_information FROM klinni_inf")
                inf = '__!\n'.join(cur.fetchone())
                cur.execute("SELECT check_list FROM klinni_inf")
                inf_2 = cur.fetchone()
                cur.execute("SELECT title FROM klinni_inf")
                inf_3 = cur.fetchone()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Как мы работаем', callback_data='2' + 'Как мы работаем'),
                         InlineKeyboardButton('Чек-Лист', url=inf_2[0]),
                         InlineKeyboardButton('Наши клинеры', callback_data='2' + 'Наши клинеры'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, photo=inf.split('__!\n')[0], caption=inf_3[0] + '\n' + inf.split('__!\n')[1], reply_markup=keyboard)
        elif data == 'Как мы работаем':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT how_work FROM klinni_inf")
                how_work = cur.fetchone()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Описание услуг'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, how_work,
                             reply_markup=keyboard)
        elif data == 'Наши клинеры':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM cleaners")
                inf = [list(i) for i in cur.fetchall()]
                cur.execute("SELECT description FROM klinni_inf")
                inf_2 = cur.fetchone()
            keyboard = InlineKeyboardMarkup()
            button = []
            for name in inf:
                button.append(InlineKeyboardButton(name[1], callback_data='1' + 'клинеры:' + name[1]))
            count = 0
            for _ in range(len(button) - 1):
                if count > len(button) - 1:
                    break
                try:
                    keyboard.row(button[count], button[count + 1], button[count + 2])
                except IndexError:
                    try:
                        keyboard.row(button[count], button[count + 1])
                    except IndexError:
                        keyboard.row(button[count])
                count += 3
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Описание услуг'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, inf_2, reply_markup=keyboard)
        elif data.split(':')[0] == 'клинеры':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM cleaners WHERE name=?", (data.split(':')[1], ))
                inf = cur.fetchone()
            keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data='1' + 'Наши клинеры'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, photo=inf[-1], caption='\n'.join(inf[2:4]), reply_markup=keyboard)
        elif data == 'Калькулятор':
            user_id[call.message.chat.id] = OrderClass()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Рассчитать уборку', callback_data='0' + 'Рассчитать уборку'),
                         InlineKeyboardButton('После ремонта', callback_data='1' + 'После ремонта'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Выберете калькулятор', reply_markup=keyboard)
        elif data == 'После ремонта':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT после_ремонта FROM klinni_inf")
                inf = cur.fetchone()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Заявка', callback_data='0' + 'Мебель'),
                         InlineKeyboardButton('Информация по уборке', callback_data='1' + 'Информация по уборке'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Калькулятор'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=inf[0].split('__!')[0],
                                  reply_markup=keyboard)
        elif data == 'Информация по уборке':
            with sqlite3.connect('klinni_base.db') as con:
                cur = con.cursor()
                cur.execute("SELECT после_ремонта FROM klinni_inf")
                inf = cur.fetchone()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Заявка', callback_data='0' + 'Мебель'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'После ремонта'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=inf[0].split('__!')[1],
                                  reply_markup=keyboard)
        elif data == 'Мебель':
            user_id[call.message.chat.id] = UserRequest()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Да', callback_data='1' 'Окна'),
                         InlineKeyboardButton('Нет', callback_data='2' + 'Окна'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='6' 'После ремонта'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='В квартире есть мебель?', reply_markup=keyboard)

        elif data == 'Окна':
            if flag == '1':
                user_id[call.message.chat.id].furniture = 'Да'
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Да', callback_data='1' 'telephone'),
                         InlineKeyboardButton('Нет', callback_data='2' + 'telephone'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='6' 'Мебель'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Нужно вымыть окна?', reply_markup=keyboard)

        elif data == 'telephone':
            if flag == '1':
                user_id[call.message.chat.id].window = 'Да'

            def user_telephone(message):
                user_id[call.message.chat.id].username = message.from_user.username
                bot.delete_message(call.message.chat.id, call.message.message_id)
                user_id[call.message.chat.id].telephone = message.text
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton('Повторить', callback_data='6' + 'telephone'),
                             InlineKeyboardButton('Дальше', callback_data='6' + 'Заявка'))
                keyboard.add(InlineKeyboardButton('Назад', callback_data='6' 'Окна'))
                bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)

            telephone = bot.edit_message_text('Введите номер телефона', call.message.chat.id,
                                            call.message.message_id)
            bot.register_next_step_handler(telephone, user_telephone)
        elif data == 'Заявка':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Отправить', callback_data='1' 'Итог'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='6' 'Меню'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Ваша заявка' + f'\nЕсть мебель: {user_id[call.message.chat.id].furniture}\n'
                                                       f'Нужно вымыть окна: {user_id[call.message.chat.id].window}\n'
                                                       f'Телефон: {user_id[call.message.chat.id].telephone}',
                                  reply_markup=keyboard)
        elif data == 'Итог':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Принять', callback_data='1' + 'Публикация отзыва'),
                         InlineKeyboardButton('Удалить', callback_data='2' + 'Удаление'))
            bot.send_message(admin_group_id,
                             'От пользователя:  ' + '@' + user_id[call.message.chat.id].username + '\nЗаявка № ' + str(order_req) +
                             f'\nЕсть мебель: {user_id[call.message.chat.id].furniture}\n'
                             f'Нужно вымыть окна: {user_id[call.message.chat.id].window}\n'
                             f'Телефон: {user_id[call.message.chat.id].telephone}',
                             reply_markup=keyboard)
            order_req += 1
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data='0' + 'Меню'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Ваша заявка принята, с вами свяжется оператор для подтверждения.\nСпасибо что выбрали нас!💕',
                                  reply_markup=keyboard)
        elif data == 'Рассчитать уборку' or data.split(' :')[0] == 'Рассчитать уборку':
            try:
                if flag == '0':
                    keyboard = InlineKeyboardMarkup()
                    buttons = [[], []]
                    for i in range(1, 11):
                        if i <= 5:
                            buttons[0].append(InlineKeyboardButton(i, callback_data='1' + 'Рассчитать уборку :' + str(i)))
                        if i > 5:
                            buttons[1].append(InlineKeyboardButton(i, callback_data='1' + 'Рассчитать уборку :' + str(i)))
                    keyboard.row(*buttons[0]).row(*buttons[1])
                    keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Калькулятор'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Выберете количество комнат', reply_markup=keyboard)
                elif flag == '1':
                    try:
                        user_id[call.message.chat.id].number_of_rooms = int(data.split(' :')[1])
                    except (IndexError, AttributeError):
                        pass
                    keyboard = InlineKeyboardMarkup()
                    buttons = [[], []]
                    for i in range(1, 11):
                        if i <= 5:
                            buttons[0].append(InlineKeyboardButton(i, callback_data='2' + 'Рассчитать уборку :' + str(i)))
                        if i > 5:
                            buttons[1].append(InlineKeyboardButton(i, callback_data='2' + 'Рассчитать уборку :' + str(i)))
                    keyboard.row(*buttons[0]).row(*buttons[1])
                    keyboard.add(InlineKeyboardButton('Назад', callback_data='0' + 'Рассчитать уборку'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Выберете количество санузлов', reply_markup=keyboard)
                elif flag == '2':
                    try:
                        user_id[call.message.chat.id].number_of_bathrooms = int(data.split(' :')[1])
                    except (IndexError, AttributeError):
                        pass
                    with sqlite3.connect('klinni_base.db') as con:
                        cur = con.cursor()
                        cur.execute("SELECT цены FROM klinni_inf")
                        inf = ''.join(cur.fetchone()[0]).split('__!\n')
                        cur.execute("SELECT время FROM klinni_inf")
                        inf_2 = ''.join(cur.fetchone()[0]).split('__!\n')
                    user_id[call.message.chat.id].cleaning_time = float(inf_2[0]) + (float(inf_2[1]) * user_id[call.message.chat.id].number_of_rooms) + (float(inf_2[2]) * user_id[call.message.chat.id].number_of_bathrooms)
                    user_id[call.message.chat.id].price = int(inf[0]) + (int(inf[1]) * user_id[call.message.chat.id].number_of_rooms) + (int(inf[2]) * user_id[call.message.chat.id].number_of_bathrooms)
                    keyboard = InlineKeyboardMarkup()
                    keyboard.row(InlineKeyboardButton('Добавить', callback_data='3' + 'Рассчитать уборку'),
                                 InlineKeyboardButton('Дальше', callback_data='6' + 'Рассчитать уборку :' + '0 :Месяц'))
                    keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Рассчитать уборку'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Хотите добавить доп услуги?\n' +
                                               f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}\n'
                                               f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}\n'
                                               f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                               f'Цена: {user_id[call.message.chat.id].price}р', reply_markup=keyboard)
                elif flag == '3':
                    try:
                        if data.split(' :')[2] == '1':
                            user_id[call.message.chat.id].additional_services.append(additional[int(data.split(' :')[1])])
                            if data.split(' :')[3] == '1':
                                user_id[call.message.chat.id].additional_services[user_id[call.message.chat.id].additional_services.index(additional[int(data.split(' :')[1])])].append(int(data.split(' :')[4]))
                                user_id[call.message.chat.id].price += additional[int(data.split(' :')[1])][2] * int(data.split(' :')[4])
                                user_id[call.message.chat.id].cleaning_time += additional[int(data.split(' :')[1])][3] * int(data.split(' :')[4])
                            else:
                                user_id[call.message.chat.id].price += additional[int(data.split(' :')[1])][1]
                                user_id[call.message.chat.id].cleaning_time += additional[int(data.split(' :')[1])][2]
                        elif data.split(' :')[2] == '2':
                            if data.split(' :')[3] == '1':
                                user_id[call.message.chat.id].price -= additional[int(data.split(' :')[1])][2] * user_id[call.message.chat.id].additional_services[user_id[call.message.chat.id].additional_services.index(additional[int(data.split(' :')[1])])][4]
                                user_id[call.message.chat.id].cleaning_time -= additional[int(data.split(' :')[1])][3] * user_id[call.message.chat.id].additional_services[user_id[call.message.chat.id].additional_services.index(additional[int(data.split(' :')[1])])][4]
                                del user_id[call.message.chat.id].additional_services[user_id[call.message.chat.id].additional_services.index(additional[int(data.split(' :')[1])])][1]
                                user_id[call.message.chat.id].additional_services.remove(additional[int(data.split(' :')[1])])
                            else:
                                user_id[call.message.chat.id].additional_services.remove(additional[int(data.split(' :')[1])])
                                user_id[call.message.chat.id].price -= additional[int(data.split(' :')[1])][1]
                                user_id[call.message.chat.id].cleaning_time -= additional[int(data.split(' :')[1])][2]
                    except IndexError:
                        pass
                    keyboard = InlineKeyboardMarkup()
                    buttons = []
                    for i in additional:
                        if i not in user_id[call.message.chat.id].additional_services:
                            buttons.append(InlineKeyboardButton(i[0], callback_data='4' + 'Рассчитать уборку :' + str(
                                additional.index(i))))
                        else:
                            buttons.append(InlineKeyboardButton('✅' + i[0], callback_data='5' + 'Рассчитать уборку :' + str(
                                additional.index(i))))
                    keyboard.row(*buttons[0:2]).row(*buttons[2:4]).row(*buttons[4:6]).row(*buttons[6:])
                    keyboard.row(InlineKeyboardButton('Дальше', callback_data='6' + 'Рассчитать уборку :' + '0 :Месяц'),
                                 InlineKeyboardButton('Назад', callback_data='2' + 'Рассчитать уборку'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='Наши доп услуги' +
                                               f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                               f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                               f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                               f'Цена: {user_id[call.message.chat.id].price}р', reply_markup=keyboard)
                elif flag == '4':
                    if additional[int(data.split(' :')[1])][0] in ['Погладим белье', 'Помоем окна',
                                                                   'Уберем на балконе'] and len(data.split(' :')) == 2:
                        keyboard = InlineKeyboardMarkup()
                        buttons = [[], [], []]
                        msg = ''
                        my_range = 7
                        if additional[int(data.split(' :')[1])][0] == 'Погладим белье':
                            my_range = 12
                            msg = ' :1 :'
                        elif additional[int(data.split(' :')[1])][0] == 'Помоем окна':
                            my_range = 16
                            msg = ' :2 :'
                        elif additional[int(data.split(' :')[1])][0] == 'Уберем на балконе':
                            buttons = [[], []]
                            msg = ' :3 :'
                        for i in range(1, my_range):
                            if i <= 5:
                                buttons[0].append(
                                    InlineKeyboardButton(i, callback_data='4' + 'Рассчитать уборку :' + data.split(' :')[
                                        1] + msg + str(i)))
                            elif 5 < i < 11:
                                buttons[1].append(
                                    InlineKeyboardButton(i, callback_data='4' + 'Рассчитать уборку :' + data.split(' :')[
                                        1] + msg + str(i)))
                            elif i > 10:
                                buttons[2].append(
                                    InlineKeyboardButton(i, callback_data='4' + 'Рассчитать уборку :' + data.split(' :')[
                                        1] + msg + str(i)))
                        if my_range == 7:
                            keyboard.row(*buttons[0], *buttons[1])
                        else:
                            keyboard.row(*buttons[0]).row(*buttons[1]).row(*buttons[2])
                        keyboard.add(InlineKeyboardButton('Назад', callback_data='3' + 'Рассчитать уборку'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f"{additional[int(data.split(' :')[1])][0]}"
                                                   f"\nЦена: {additional[int(data.split(' :')[1])][2]}р"
                                                   f"\nВремя: {additional[int(data.split(' :')[1])][3]}ч"
                                              , reply_markup=keyboard)
                    else:
                        try:
                            if data.split(' :')[2] in ['1', '2', '3']:
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(InlineKeyboardButton('Добавить', callback_data='3' + 'Рассчитать уборку :'
                                                                                            + data.split(' :')[
                                                                                                1] + ' :1 :1 :' +
                                                                                            data.split(' :')[3]),
                                             InlineKeyboardButton('Назад', callback_data='3' + 'Рассчитать уборку'))
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text=f"{additional[int(data.split(' :')[1])][0]}"
                                                           f"\nЦена: {additional[int(data.split(' :')[1])][2] * int(data.split(' :')[3])} р"
                                                           f"\nВремя: {additional[int(data.split(' :')[1])][3] * int(data.split(' :')[3])}ч"
                                                      , reply_markup=keyboard)
                        except IndexError:
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Добавить',
                                                              callback_data='3' + 'Рассчитать уборку :' + data.split(' :')[
                                                                  1] + ' :1 :2'),
                                         InlineKeyboardButton('Назад', callback_data='3' + 'Рассчитать уборку'))
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=f"{additional[int(data.split(' :')[1])][0]}"
                                                       f"\nЦена: {additional[int(data.split(' :')[1])][1]}р"
                                                       f"\nВремя: {additional[int(data.split(' :')[1])][2]}ч"
                                                  , reply_markup=keyboard)
                elif flag == '5':
                    keyboard = InlineKeyboardMarkup()
                    if additional[int(data.split(' :')[1])][0] in ['Погладим белье', 'Помоем окна',
                                                                   'Уберем на балконе'] and len(data.split(' :')) == 2:
                        keyboard.row(
                            InlineKeyboardButton('Убрать', callback_data='3' + 'Рассчитать уборку :' + data.split(' :')[
                                1] + ' :2 :1'),
                            InlineKeyboardButton('Назад', callback_data='3' + 'Рассчитать уборку'))
                    else:
                        keyboard.row(
                            InlineKeyboardButton('Убрать', callback_data='3' + 'Рассчитать уборку :' + data.split(' :')[
                                1] + ' :2 :2'),
                            InlineKeyboardButton('Назад', callback_data='3' + 'Рассчитать уборку'))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"{additional[int(data.split(' :')[1])][0]}"
                                               f"\nЦена: {additional[int(data.split(' :')[1])][1]}р"
                                               f"\nВремя: {additional[int(data.split(' :')[1])][2]}ч"
                                          , reply_markup=keyboard)
                elif flag == '6':
                    if data.split(' :')[2] == 'Месяц':
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Октябрь', callback_data='6' + 'Рассчитать уборку :' + str(
                            time.strptime(time.ctime(time.time())).tm_mon) + ' :День'),
                                     InlineKeyboardButton('Ноябрь', callback_data='6' + 'Рассчитать уборку :' + str(
                                         time.strptime(time.ctime(time.time())).tm_mon + 1) + ' :День'),
                                     InlineKeyboardButton('Декабрь', callback_data='6' + 'Рассчитать уборку :' + str(
                                         time.strptime(time.ctime(time.time())).tm_mon + 2) + ' :День'))
                        keyboard.add(InlineKeyboardButton('Назад', callback_data='2' + 'Рассчитать уборку'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выберете месяц', reply_markup=keyboard)
                    elif data.split(' :')[2] == 'День':
                        year = time.strptime(time.ctime(time.time())).tm_year
                        calen = calendar.TextCalendar()
                        if data.split(' :')[1] == 'Назад':
                            month = user_id[call.message.chat.id].month
                        else:
                            month = int(data.split(' :')[1])
                        if month == 13 or month == 14:
                            month = month - 12
                            year += 1
                        days = calen.formatmonth(year, month)[40:].strip().replace('\n', ' ').replace('  ', ' ').split(' ')
                        keyboard = InlineKeyboardMarkup()
                        buttons = [[], [], [], [], []]
                        for i in days:
                            i = int(i)
                            if i <= 7:
                                buttons[0].append(
                                    InlineKeyboardButton(i, callback_data='6' + 'Рассчитать уборку :' + str(i) + ' :Время'))
                            elif 7 < i < 15:
                                buttons[1].append(
                                    InlineKeyboardButton(i, callback_data='6' + 'Рассчитать уборку :' + str(i) + ' :Время'))
                            elif 15 <= i < 22:
                                buttons[2].append(
                                    InlineKeyboardButton(i, callback_data='6' + 'Рассчитать уборку :' + str(i) + ' :Время'))
                            elif 22 <= i < 29:
                                buttons[3].append(
                                    InlineKeyboardButton(i, callback_data='6' + 'Рассчитать уборку :' + str(i) + ' :Время'))
                            elif i > 28:
                                buttons[4].append(InlineKeyboardButton(i, callback_data='6' 'Рассчитать уборку :' + str(i) + ' :Время'))
                        keyboard.row(*buttons[0]).row(*buttons[1]).row(*buttons[2]).row(*buttons[3]).row(*buttons[4])
                        keyboard.add(InlineKeyboardButton('Назад', callback_data='6' + 'Рассчитать уборку :' + '0 :Месяц'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выберете день', reply_markup=keyboard)
                        user_id[call.message.chat.id].year = year
                        user_id[call.message.chat.id].month = month
                    if data.split(' :')[2] == 'Время':
                        keyboard = InlineKeyboardMarkup()
                        buttons = [[], [], [], []]
                        count = 9
                        for i in range(3):
                            for g in range(7):
                                buttons[i].append(InlineKeyboardButton(str('%.2f' % count).replace('.', ':'),
                                                                       callback_data='6' 'Рассчитать уборку :' + str(
                                                                           '%.2f' % count).replace('.', ':') + ' :Регу'))
                                if isinstance(count, int):
                                    count += 0.30
                                else:
                                    count = int(count + 0.70)
                                if str('%.2f' % count).replace('.', ':') == '18:30':
                                    break
                        keyboard.row(*buttons[0]).row(*buttons[1]).row(*buttons[2]).row(*buttons[3])
                        keyboard.add(
                            InlineKeyboardButton('Назад', callback_data='6' + 'Рассчитать уборку :Назад' + ' :День'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Выберете время', reply_markup=keyboard)
                        user_id[call.message.chat.id].day = data.split(' :')[1]
                    if data.split(' :')[2] == 'Регу':
                        user_id[call.message.chat.id].regularity_of_cleaning = []
                        if user_id[call.message.chat.id].time == '':
                            user_id[call.message.chat.id].time = data.split(' :')[1]
                        user_id[
                            call.message.chat.id].the_date = f'{user_id[call.message.chat.id].day}/{user_id[call.message.chat.id].month}/{user_id[call.message.chat.id].year}'
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Раз в неделю\nЦена -15%',
                                                          callback_data='6' 'Рассчитать уборку :' + '15' + ' :Адрес'),
                                     InlineKeyboardButton('Раз в 2 недели\nЦена -10%',
                                                          callback_data='6' 'Рассчитать уборку :' + '10' + ' :Адрес'))
                        keyboard.row(InlineKeyboardButton('Раз в месяц\nЦена -7%',
                                                          callback_data='6' 'Рассчитать уборку :' + '7' + ' :Адрес'),
                                     InlineKeyboardButton('1 Раз или первый раз',
                                                          callback_data='6' 'Рассчитать уборку :' + '0' + ' :Адрес'))
                        keyboard.add(
                            InlineKeyboardButton('Назад', callback_data='6' + 'Рассчитать уборку :Назад' + ' :Время'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                                   f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                                   f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                                   f'Цена: {user_id[call.message.chat.id].price}р\n'
                                                   f'Дата: {user_id[call.message.chat.id].the_date}\n'
                                                   f'Время: {user_id[call.message.chat.id].time}', reply_markup=keyboard)
                    if data.split(' :')[2] == 'Адрес':
                        if user_id[call.message.chat.id].regularity_of_cleaning == []:
                            if data.split(' :')[1] == '15':
                                user_id[call.message.chat.id].regularity_of_cleaning = ['Раз в неделю', 15]
                            elif data.split(' :')[1] == '10':
                                user_id[call.message.chat.id].regularity_of_cleaning = ['Раз в 2 недели', 10]
                            elif data.split(' :')[1] == '7':
                                user_id[call.message.chat.id].regularity_of_cleaning = ['Раз в месяц', 7]
                            else:
                                user_id[call.message.chat.id].regularity_of_cleaning = ['1 Раз или первый раз', 0]

                        def user_address(message):
                            try:
                                if message.text == '/start':
                                    menu(message, message.chat.id)
                                    return
                                bot.delete_message(call.message.chat.id, call.message.message_id)
                                user_id[call.message.chat.id].address = message.text
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(InlineKeyboardButton('Повторить',
                                                                  callback_data='6' 'Рассчитать уборку :' + '0' + ' :Адрес'),
                                             InlineKeyboardButton('Дальше',
                                                                  callback_data='6' + 'Рассчитать уборку :' + '0' + ' :ФИО'))
                                keyboard.add(
                                    InlineKeyboardButton('Назад',
                                                         callback_data='6' 'Рассчитать уборку :' + '0' + ' :Регу'))
                                bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text,
                                                 reply_markup=keyboard)
                            except KeyError:
                                menu(message, message.chat.id)

                        if data.split(' :')[1] != '15':
                            with sqlite3.connect('klinni_base.db') as con:
                                cur = con.cursor()
                                cur.execute("SELECT * FROM user_id WHERE chat_id=?", (call.message.chat.id,))
                                res = cur.fetchall()
                            if len(res) > 0:
                                user_id[call.message.chat.id].username = res[0][1]
                                user_id[call.message.chat.id].address, user_id[call.message.chat.id].full_name, user_id[call.message.chat.id].telephone, user_id[call.message.chat.id].email = res[0][3:]
                                keyboard = InlineKeyboardMarkup()
                                keyboard.add(InlineKeyboardButton('Использовать старые данные', callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Итог'))
                                keyboard.add(InlineKeyboardButton('Ввести по новой', callback_data='6' 'Рассчитать уборку :' + '15' + ' :Адрес'))
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text=f'Контактные данные:\n'
                                                           f'Адресс: {user_id[call.message.chat.id].address}\n'
                                                           f'ФИО: {user_id[call.message.chat.id].full_name}\n'
                                                           f'Телефон: {user_id[call.message.chat.id].telephone}\n'
                                                           f'Почта: {user_id[call.message.chat.id].email}\n',
                                                      reply_markup=keyboard)
                        else:
                            address = bot.edit_message_text('Введите Адрес квартиры', call.message.chat.id,
                                                            call.message.message_id)
                            bot.register_next_step_handler(address, user_address)

                    if data.split(' :')[2] == 'ФИО':
                        def user_full_name(message):
                            try:
                                if message.text == '/start':
                                    menu(message, message.chat.id)
                                    return
                                bot.delete_message(call.message.chat.id, call.message.message_id)
                                user_id[call.message.chat.id].full_name = message.text
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(
                                    InlineKeyboardButton('Повторить', callback_data='6' 'Рассчитать уборку :' + '0' + ' :ФИО'),
                                    InlineKeyboardButton('Дальше',
                                                         callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Телефон'))
                                keyboard.add(
                                    InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :Адрес'))
                                bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)
                            except KeyError:
                                menu(message, message.chat.id)

                        full_name = bot.edit_message_text('Введите ФИО', call.message.chat.id,
                                                          call.message.message_id)
                        bot.register_next_step_handler(full_name, user_full_name)
                    if data.split(' :')[2] == 'Телефон':
                        def user_telephone(message):
                            try:
                                if message.text == '/start':
                                    menu(message, message.chat.id)
                                    return
                                bot.delete_message(call.message.chat.id, call.message.message_id)
                                user_id[call.message.chat.id].telephone = message.text
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(InlineKeyboardButton('Повторить',
                                                                  callback_data='6' 'Рассчитать уборку :' + '0' + ' :Телефон'),
                                             InlineKeyboardButton('Дальше',
                                                                  callback_data='6' + 'Рассчитать уборку :' + '0' + ' :email'))
                                keyboard.add(
                                    InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :ФИО'))
                                bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)
                            except KeyError:
                                menu(message, message.chat.id)

                        telephone = bot.edit_message_text('Введите свой контактный телефон', call.message.chat.id,
                                                          call.message.message_id)
                        bot.register_next_step_handler(telephone, user_telephone)
                    if data.split(' :')[2] == 'email':
                        def user_email(message):
                            try:
                                if message.text == '/start':
                                    menu(message, message.chat.id)
                                    return
                                bot.delete_message(call.message.chat.id, call.message.message_id)
                                user_id[call.message.chat.id].email = message.text
                                user_id[call.message.chat.id].username = message.from_user.username
                                user_id[call.message.chat.id].chat_id = message.chat.id
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(InlineKeyboardButton('Повторить',
                                                                  callback_data='6' 'Рассчитать уборку :' + '0' + ' :email'),
                                             InlineKeyboardButton('Дальше',
                                                                  callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Итог'))
                                keyboard.add(
                                    InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :Телефон'))
                                bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)
                            except KeyError:
                                menu(message, message.chat.id)

                        email = bot.edit_message_text('Введите свою почту', call.message.chat.id,
                                                      call.message.message_id)
                        bot.register_next_step_handler(email, user_email)
                    if data.split(' :')[2] == 'Итог':
                        user_id[call.message.chat.id].total = float(user_id[call.message.chat.id].price) - (
                                    (float(user_id[call.message.chat.id].price) / 100) *
                                    user_id[call.message.chat.id].regularity_of_cleaning[1])
                        if user_id[call.message.chat.id].promo_code == []:
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Заказать', callback_data='6' 'Рассчитать уборку :' + '15' + ' :Финал'),
                                         InlineKeyboardButton('Промокод', callback_data='6' 'Рассчитать уборку :' + '10' + ' :Промокод'))
                            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' 'Рассчитать уборку :' + '0' + ' :Адрес'))
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=text_res(call, user_id),
                                                  reply_markup=keyboard)
                        else:
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Заказать',
                                                              callback_data='6' 'Рассчитать уборку :' + '15' + ' :Финал'),
                                         InlineKeyboardButton('Назад',
                                                              callback_data='1' 'Рассчитать уборку :' + '0' + ' :Адрес'))
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=text_res(call, user_id, promo=1),
                                                  reply_markup=keyboard)
                    if data.split(' :')[2] == 'Промокод':
                        def user_promo_code(message):
                            if message.text == '/start':
                                menu(message, message.chat.id)
                                return
                            bot.delete_message(call.message.chat.id, call.message.message_id)
                            if message.text in promo_code and user_id[call.message.chat.id].promo_code == []:
                                user_id[call.message.chat.id].promo_code = [message.text, promo_code[message.text]]
                                user_id[call.message.chat.id].total = float(user_id[call.message.chat.id].total) - (
                                            (float(user_id[call.message.chat.id].price) / 100) *
                                            user_id[call.message.chat.id].promo_code[1])
                                keyboard = InlineKeyboardMarkup()
                                keyboard.row(InlineKeyboardButton('Заказать',
                                                                  callback_data='6' 'Рассчитать уборку :' + '15' + ' :Финал'))
                                keyboard.add(InlineKeyboardButton('Назад',
                                                                  callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Итог'))
                                bot.send_message(chat_id=call.message.chat.id,
                                                 text=text_res(call, user_id, promo=1),
                                                      reply_markup=keyboard)
                            else:
                                keyboard = InlineKeyboardMarkup()
                                keyboard.add(InlineKeyboardButton('Назад',
                                                                  callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Итог'))
                                bot.send_message(call.message.chat.id, 'Такого промокода нет\nИли вы его уже использовали',
                                                 reply_markup=keyboard)

                        code = bot.edit_message_text('Введите промокод', call.message.chat.id,
                                                     call.message.message_id)
                        bot.register_next_step_handler(code, user_promo_code)
                    if data.split(' :')[2] == 'Финал':
                        inf_4 = ('@' + user_id[call.message.chat.id].username, str(user_id[call.message.chat.id].chat_id),
                                 user_id[call.message.chat.id].address, user_id[call.message.chat.id].full_name,
                                 user_id[call.message.chat.id].telephone, user_id[call.message.chat.id].email)
                        db_update(inf_4=inf_4)
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Принять', callback_data='1' + 'Принять'),
                                     InlineKeyboardButton('Удалить', callback_data='2' + 'Удаление'))
                        if user_id[call.message.chat.id].promo_code == []:
                            bot.send_message(admin_group_id,
                                             'От пользователя:  ' + '@' + user_id[call.message.chat.id].username + '\nЗаказ № ' + str(order) +
                                             text_res(call, user_id),
                                             reply_markup=keyboard)
                        else:
                            bot.send_message(admin_group_id,
                                             'От пользователя:  ' + '@' + user_id[
                                                 call.message.chat.id].username + '\nЗаказ № ' + str(order) +
                                             text_res(call, user_id, promo=1),
                                             reply_markup=keyboard)
                        order += 1
                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton('Назад', callback_data='0' + 'Меню'))
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Ваша заявка принята, с вами свяжется оператор для подтверждения.\nСпасибо что выбрали нас!💕',
                                              reply_markup=keyboard)
                        return order
            except KeyError:
                user_id[call.message.chat.id] = OrderClass()
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton('Рассчитать уборку', callback_data='0' + 'Рассчитать уборку'),
                             InlineKeyboardButton('После ремонта', callback_data='1' + 'После ремонта'))
                keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Что-то пошло не так\nВыберете калькулятор', reply_markup=keyboard)
    except KeyError:
        menu(call, call.message.chat.id)


bot.infinity_polling()
