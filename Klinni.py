import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_req
from add_class import OrderClass, UserRequest
import time
import calendar
from math import ceil, floor

bot = telebot.TeleBot('5502235861:AAHzqGs8cakisXDVOA4TnC87yIIh7xfPiIo')
admin_group_id = -884604288
reviews_group_id = -850436301
admin_id = [428955934, 938312974]
user_id = {}
additional = [['Внутри холодильника', 25, 1], ['Внутри духовки', 25, 1], ['Внутри кухонных шкафов', 25, 1],
              ['Помоем посуду', 10, 0.5], ['Внутри микроволновки', 20, 0.5], ['Погладим белье, ч', 20, 1],
              ['Помоем окна, шт', 15, 0.5], ['Уберем на балконе, шт', 20, 1]]
promo_code = {'123': 15, '1234': 20}
order = 1
order_req = 1


def fs(st):
    return st[0]


def dt(s):
    s = s[1:]
    return s


def menu(call, user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Калькулятор', callback_data='0' + 'Калькулятор'),
                 InlineKeyboardButton('Описание услуг', callback_data='1' + 'Описание услуг'),
                 InlineKeyboardButton('Отзывы', callback_data='0' + 'Отзывы'))
    if user_id in admin_id:
        keyboard.row(InlineKeyboardButton('Сообщение администратору', callback_data='0' + 'Сообщение'),
                     InlineKeyboardButton('Административная панель', callback_data='0' + 'Административная'))
        keyboard.add(InlineKeyboardButton('Наш сайт', url='http://cleanny.by/'))
    else:
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
    flag = fs(call.data)
    data = dt(call.data)
    try:
        if data == 'Отзывы':
            def reviews(message):
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
                         InlineKeyboardButton('Обновить БД ', callback_data='1' + 'Обновить БД '),
                         InlineKeyboardButton('Статистика', callback_data='1' + 'Статистика'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            bot.edit_message_text('Панель администратора', call.message.chat.id, call.message.message_id,
                                  reply_markup=keyboard)
        elif data == 'Описание услуг':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Как мы работаем', callback_data='2' + 'Как мы работаем'),
                         InlineKeyboardButton('Чек-Лист', url=bot_req.check_list()),
                         InlineKeyboardButton('Наши клинеры', callback_data='2' + 'Наши клинеры'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            inf = bot_req.general_information()
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, photo=inf[0], caption='\n'.join(inf[1]), reply_markup=keyboard)
        elif data == 'Как мы работаем':
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Описание услуг'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, '\n'.join(bot_req.how_work()),
                             reply_markup=keyboard)
        elif data == 'Наши клинеры':
            keyboard = InlineKeyboardMarkup()
            inf = bot_req.cleaners()
            button = []
            for name in inf[2]:
                button.append(InlineKeyboardButton(name, callback_data='1' + 'клинеры:' + name))
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
            bot.send_message(call.message.chat.id, inf[0] + '\n' + inf[1], reply_markup=keyboard)
        elif data.split(':')[0] == 'клинеры':
            inf = bot_req.cleaners()[2][data.split(':')[1]].split('\n')
            keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data='1' + 'Наши клинеры'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, photo=inf[-1], caption='\n'.join(inf[0:2]), reply_markup=keyboard)
        elif data == 'Калькулятор':
            user_id[call.message.chat.id] = OrderClass()
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Рассчитать уборку', callback_data='0' + 'Рассчитать уборку'),
                         InlineKeyboardButton('После ремонта', callback_data='1' + 'После ремонта'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Меню'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Выберете калькулятор', reply_markup=keyboard)
        elif data == 'После ремонта':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Заявка', callback_data='0' + 'Мебель'),
                         InlineKeyboardButton('Информация по уборке', callback_data='1' + 'Информация по уборке'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'Калькулятор'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Забронировать уборку заранее\nВы можете оставить заявку и получить скидку 5%.\n'
                                       'Даже если вы не знаете точной даты уборки, у вас уже будет гарантия лучшей цены.',
                                  reply_markup=keyboard)
        elif data == 'Информация по уборке':
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton('Заявка', callback_data='0' + 'Мебель'))
            keyboard.add(InlineKeyboardButton('Назад', callback_data='1' + 'После ремонта'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Цена уборки зависит от числа окон, санузлов и наличия мебели, но почти всегда находится в этом диапазоне.\n'
                                       'Однокомнатная: 250-300 BYN\n'
                                       'Двухкомнатная : 300-350 BYN\n'
                                       'Трехкомнатная : 350-400 BYN\n'
                                       'Четырехкомнатная : 400-450 BYN',
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
                    if user_id[call.message.chat.id].cleaning_time == 0:
                        user_id[call.message.chat.id].cleaning_time = 1.5 + (
                                    1 * user_id[call.message.chat.id].number_of_rooms) + (0.5 * user_id[
                            call.message.chat.id].number_of_bathrooms)
                        user_id[call.message.chat.id].price = 31 + (14 * user_id[call.message.chat.id].number_of_rooms) + (
                                    20 * user_id[call.message.chat.id].number_of_bathrooms)
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
                                user_id[call.message.chat.id].additional_services[
                                    user_id[call.message.chat.id].additional_services.index(
                                        additional[int(data.split(' :')[1])])].append(int(data.split(' :')[4]))
                                user_id[call.message.chat.id].price += additional[int(data.split(' :')[1])][1] * int(
                                    data.split(' :')[4])
                                user_id[call.message.chat.id].cleaning_time += additional[int(data.split(' :')[1])][
                                                                                   2] * int(data.split(' :')[4])
                            else:
                                user_id[call.message.chat.id].price += additional[int(data.split(' :')[1])][1]
                                user_id[call.message.chat.id].cleaning_time += additional[int(data.split(' :')[1])][2]
                        elif data.split(' :')[2] == '2':
                            if data.split(' :')[3] == '1':
                                user_id[call.message.chat.id].price -= additional[int(data.split(' :')[1])][1] * \
                                                                       user_id[call.message.chat.id].additional_services[
                                                                           user_id[
                                                                               call.message.chat.id].additional_services.index(
                                                                               additional[int(data.split(' :')[1])])][3]
                                user_id[call.message.chat.id].cleaning_time -= additional[int(data.split(' :')[1])][2] * \
                                                                               user_id[
                                                                                   call.message.chat.id].additional_services[
                                                                                   user_id[
                                                                                       call.message.chat.id].additional_services.index(
                                                                                       additional[
                                                                                           int(data.split(' :')[1])])][3]
                                del user_id[call.message.chat.id].additional_services[
                                    user_id[call.message.chat.id].additional_services.index(
                                        additional[int(data.split(' :')[1])])][3]
                                user_id[call.message.chat.id].additional_services.remove(
                                    additional[int(data.split(' :')[1])])
                            else:
                                user_id[call.message.chat.id].additional_services.remove(
                                    additional[int(data.split(' :')[1])])
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
                    if additional[int(data.split(' :')[1])][0] in ['Погладим белье, ч', 'Помоем окна, шт',
                                                                   'Уберем на балконе, шт'] and len(data.split(' :')) == 2:
                        keyboard = InlineKeyboardMarkup()
                        buttons = [[], [], []]
                        msg = ''
                        my_range = 7
                        if additional[int(data.split(' :')[1])][0] == 'Погладим белье, ч':
                            my_range = 12
                            msg = ' :1 :'
                        elif additional[int(data.split(' :')[1])][0] == 'Помоем окна, шт':
                            my_range = 16
                            msg = ' :2 :'
                        elif additional[int(data.split(' :')[1])][0] == 'Уберем на балконе, шт':
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
                                                   f"\nЦена: {additional[int(data.split(' :')[1])][1]}р"
                                                   f"\nВремя: {additional[int(data.split(' :')[1])][2]}ч"
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
                                                           f"\nЦена: {additional[int(data.split(' :')[1])][1] * int(data.split(' :')[3])} р"
                                                           f"\nВремя: {additional[int(data.split(' :')[1])][2] * int(data.split(' :')[3])}ч"
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
                    if additional[int(data.split(' :')[1])][0] in ['Погладим белье, ч', 'Помоем окна, шт',
                                                                   'Уберем на балконе, шт'] and len(data.split(' :')) == 2:
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
                                buttons[4].append(InlineKeyboardButton(i, callback_data='6' + str(i) + ' :Время'))
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
                            bot.delete_message(call.message.chat.id, call.message.message_id)
                            user_id[call.message.chat.id].adress = message.text
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Повторить',
                                                              callback_data='6' 'Рассчитать уборку :' + '0' + ' :Адрес'),
                                         InlineKeyboardButton('Дальше',
                                                              callback_data='6' + 'Рассчитать уборку :' + '0' + ' :ФИО'))
                            keyboard.add(
                                InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :Регу'))
                            bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)

                        address = bot.edit_message_text('Введите Адрес квартиры', call.message.chat.id,
                                                        call.message.message_id)
                        bot.register_next_step_handler(address, user_address)
                    if data.split(' :')[2] == 'ФИО':
                        def user_full_name(message):
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

                        full_name = bot.edit_message_text('Введите ФИО', call.message.chat.id,
                                                          call.message.message_id)
                        bot.register_next_step_handler(full_name, user_full_name)
                    if data.split(' :')[2] == 'Телефон':
                        def user_telephone(message):
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

                        telephone = bot.edit_message_text('Введите свой контактный телефон', call.message.chat.id,
                                                          call.message.message_id)
                        bot.register_next_step_handler(telephone, user_telephone)
                    if data.split(' :')[2] == 'email':
                        def user_email(message):
                            bot.delete_message(call.message.chat.id, call.message.message_id)
                            user_id[call.message.chat.id].email = message.text
                            user_id[call.message.chat.id].username = message.from_user.username
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Повторить',
                                                              callback_data='6' 'Рассчитать уборку :' + '0' + ' :email'),
                                         InlineKeyboardButton('Дальше',
                                                              callback_data='6' + 'Рассчитать уборку :' + '0' + ' :Итог'))
                            keyboard.add(
                                InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :Телефон'))
                            bot.send_message(call.message.chat.id, 'Все верно?\n' + message.text, reply_markup=keyboard)

                        email = bot.edit_message_text('Введите свою почту', call.message.chat.id,
                                                      call.message.message_id)
                        bot.register_next_step_handler(email, user_email)
                    if data.split(' :')[2] == 'Итог':
                        user_id[call.message.chat.id].total = float(user_id[call.message.chat.id].price) - (
                                    (float(user_id[call.message.chat.id].price) / 100) *
                                    user_id[call.message.chat.id].regularity_of_cleaning[1])
                        if user_id[call.message.chat.id].promo_code == []:
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Заказать',
                                                              callback_data='6' 'Рассчитать уборку :' + '15' + ' :Финал'),
                                         InlineKeyboardButton('Промокод',
                                                              callback_data='6' 'Рассчитать уборку :' + '10' + ' :Промокод'))
                            keyboard.add(
                                InlineKeyboardButton('Назад', callback_data='6' 'Рассчитать уборку :' + '0' + ' :email'))
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                                       f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                                       f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                                       f'Цена: {user_id[call.message.chat.id].price}р\n'
                                                       f'Дата: {user_id[call.message.chat.id].the_date}\n'
                                                       f'Время: {user_id[call.message.chat.id].time}\n'
                                                       f'ФИО: {user_id[call.message.chat.id].full_name}\n'
                                                       f'Адрес: {user_id[call.message.chat.id].adress}\n'
                                                       f'Телефон: {user_id[call.message.chat.id].telephone}\n'
                                                       f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'
                                                       f'К оплате: {ceil(user_id[call.message.chat.id].total)}',
                                                  reply_markup=keyboard)
                        else:
                            keyboard = InlineKeyboardMarkup()
                            keyboard.row(InlineKeyboardButton('Заказать',
                                                              callback_data='6' 'Рассчитать уборку :' + '15' + ' :Финал'),
                                         InlineKeyboardButton('Назад',
                                                              callback_data='6' 'Рассчитать уборку :' + '0' + ' :email'))
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                                       f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                                       f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                                       f'Цена: {user_id[call.message.chat.id].price}р\n'
                                                       f'Дата: {user_id[call.message.chat.id].the_date}\n'
                                                       f'Время: {user_id[call.message.chat.id].time}\n'
                                                       f'ФИО: {user_id[call.message.chat.id].full_name}\n'
                                                       f'Адрес: {user_id[call.message.chat.id].adress}\n'
                                                       f'Телефон: {user_id[call.message.chat.id].telephone}\n'
                                                       f'Почта : {user_id[call.message.chat.id].email}'
                                                       f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'
                                                       f'Сумма скидки за промокод: {floor((float(user_id[call.message.chat.id].total) / 100) * user_id[call.message.chat.id].promo_code[1])}р\n'
                                                       f'К оплате: {ceil(user_id[call.message.chat.id].total)}р',
                                                  reply_markup=keyboard)
                    if data.split(' :')[2] == 'Промокод':
                        def user_promo_code(message):
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
                                                 text=f'Ваш заказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                                      f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                                      f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                                      f'Цена: {user_id[call.message.chat.id].price}р\n'
                                                      f'Дата: {user_id[call.message.chat.id].the_date}\n'
                                                      f'Время: {user_id[call.message.chat.id].time}\n'
                                                      f'ФИО: {user_id[call.message.chat.id].full_name}\n'
                                                      f'Адрес: {user_id[call.message.chat.id].adress}\n'
                                                      f'Телефон: {user_id[call.message.chat.id].telephone}\n'
                                                      f'Почта : {user_id[call.message.chat.id].email}'
                                                      f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'
                                                      f'Сумма скидки за промокод: {floor((float(user_id[call.message.chat.id].total) / 100) * user_id[call.message.chat.id].promo_code[1])}р\n'
                                                      f'К оплате: {ceil(user_id[call.message.chat.id].total)}р',
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
                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(InlineKeyboardButton('Принять', callback_data='1' + 'Публикация отзыва'),
                                     InlineKeyboardButton('Удалить', callback_data='2' + 'Удаление'))
                        bot.send_message(admin_group_id,
                                         'От пользователя:  ' + '@' + user_id[call.message.chat.id].username + '\nЗаказ № ' + str(order) +
                                         f'\nЗаказ:\nКоличество комнат: {user_id[call.message.chat.id].number_of_rooms}шт\n'
                                         f'Количество санузлов: {user_id[call.message.chat.id].number_of_bathrooms}шт\n'
                                         f'Время уборки: {user_id[call.message.chat.id].cleaning_time}ч\n'
                                         f'Цена: {user_id[call.message.chat.id].price}р\n'
                                         f'Дата: {user_id[call.message.chat.id].the_date}\n'
                                         f'Время: {user_id[call.message.chat.id].time}\n'
                                         f'ФИО: {user_id[call.message.chat.id].full_name}\n'
                                         f'Адрес: {user_id[call.message.chat.id].adress}\n'
                                         f'Телефон: {user_id[call.message.chat.id].telephone}\n'
                                         f'Почта : {user_id[call.message.chat.id].email}'
                                         f'Сумма скидки за регулярность: {floor((float(user_id[call.message.chat.id].price) / 100) * user_id[call.message.chat.id].regularity_of_cleaning[1])}р\n'
                                         f'Сумма скидки за промокод: {floor((float(user_id[call.message.chat.id].total) / 100) * user_id[call.message.chat.id].promo_code[1])}\n'
                                         f'К оплате: {ceil(user_id[call.message.chat.id].total)}р',
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
