#!/usr/bin/env python
import config
import telebot
from telebot import types
import logging
import datetime
import scraper as src
from timetable_keeper import ScheduleHolder

logging.basicConfig(level=logging.INFO)

# proxy for connection#
# apihelper.proxy = {'https': '173.249.43.27:3128'}
bot = telebot.TeleBot(config.TOKEN)

req = src.Scraper()
faculty, faculty_swapped = req.get_faculty()  # dict with data in format: "name of faculty": id of faculty
course, course_swapped = {}, {}  # dict with data in format: "name of course": id of course
groups, groups_swapped = {}, {}  # dict with data in format: "name of group": id of group

schedule = ScheduleHolder()


def choose_faculty():
    items = []
    for val in faculty:
        items.append(types.InlineKeyboardButton(val, callback_data='facul' + str(faculty[val])))

    return items


def choose_course():
    items = []
    for year in course:
        items.append(types.InlineKeyboardButton(year, callback_data='year' + str(course[year])))
    items.append(types.InlineKeyboardButton("Назад", callback_data='prev_fac'))
    return items


def choose_group():
    items = []
    for group in groups:
        items.append(types.InlineKeyboardButton(group, callback_data='group' + str(groups[group])))
    items.append(types.InlineKeyboardButton("Назад", callback_data='fac_prev'))
    return items


@bot.message_handler(commands=['start'])
def welcome(message):
    #sti = open('static/welcome.webp', 'rb')
    #bot.send_sticker(message.chat.id, sti)
    #logging.info(f"User - {call.}")
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Выбор группы")
    # item2 = types.KeyboardButton("Как дела?")
    markup.add(item1)

    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный "
                                      "чтобы быть подопытным кроликом".format(message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def buttons_logic(message):
    if message.chat.type == 'private':
        if message.text == 'Выбор группы':
            markup = types.InlineKeyboardMarkup(row_width=3)
            items = choose_faculty()
            markup.add(*items)
            bot.send_message(message.chat.id, 'Выберете факультет', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить')


# Call to display courses available at the faculty (edit message with faculty list)
@bot.callback_query_handler(func=lambda call: call.data.startswith('facul'))
def callback_inline_course(call):
    global course, course_swapped, schedule
    try:
        if call.message:
            schedule.faculty_id = int(call.data[5:])
            logging.info(f'Nickname - {call.from_user.username}')
            markup = types.InlineKeyboardMarkup(row_width=1)
            course, course_swapped = req.get_courses(schedule.faculty_id)
            items = choose_course()
            markup.add(*items)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберете курс", reply_markup=markup)
    except Exception as e:
        print(repr(e))


# Call to display groups in course (edit message with course list)
@bot.callback_query_handler(func=lambda call: call.data.startswith('year'))
def callback_inline_group(call):
    global groups, groups_swapped, schedule
    try:
        if call.message:
            # bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='Hello Test ' + call.data[4:])
            schedule.course_id = int(call.data[4:])
            markup = types.InlineKeyboardMarkup(row_width=2)
            groups, groups_swapped = req.get_groups(schedule.faculty_id, schedule.course_id)
            items = choose_group()
            markup.add(*items)
            logging.info(f'User - {call.from_user.first_name}\n'
                         f'Nickname - {call.from_user.username}\n'
                         f'Selected course - {course_swapped[str(schedule.course_id)]}')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите группу", reply_markup=markup)
    except Exception as e:
        print(repr(e))


# Call to save data after choosing a group
@bot.callback_query_handler(func=lambda call: call.data.startswith('group'))
def callback_hold_data(call):
    global schedule  # group_id
    try:
        if call.message:
            schedule.group_id = int(call.data[5:])
            markup = types.InlineKeyboardMarkup(row_width=2)
            items = [types.InlineKeyboardButton("Назад", callback_data='last'),
                     types.InlineKeyboardButton("Сохранить", callback_data='save')]
            message_text = f"Выбранный факультет - {faculty_swapped[str(schedule.faculty_id)]}\n" \
                           f"Выбранный курс - {course_swapped[str(schedule.course_id)]}\n" \
                           f"Выбранная группа - {groups_swapped[str(schedule.group_id)]}"
            markup.add(*items)
            # bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='Hello Test ' + call.data[5:])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=message_text, reply_markup=markup)
    except Exception as e:
        print(repr(e))


@bot.callback_query_handler(func=lambda call: call.data.startswith('save'))
def callback_confirm_data(call):
    global schedule
    try:
        mes = src.get_timetable(schedule.group_id, '11.09.2020')
        logging.info(f'User - {call.from_user.first_name}\n')
        bot.send_message(call.message.chat.id, mes)
        
    except Exception as e:
        print(repr(e))


# Call to display step before choosing course (button shown in course list)
@bot.callback_query_handler(func=lambda call: call.data.startswith('prev'))
def callback_faculty_step(call):
    global course, schedule
    try:
        if call.message:
            course.clear()
            schedule.course_id = 0
            markup = types.InlineKeyboardMarkup(row_width=3)
            items = choose_faculty()
            markup.add(*items)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите группу", reply_markup=markup)
    except Exception as e:
        print(repr(e))


# Call to display step before choosing group (button shown in groups list)
@bot.callback_query_handler(func=lambda call: call.data.startswith('fac_prev'))
def callback_faculty_step(call):
    global groups, schedule
    try:
        if call.message:
            groups.clear()
            schedule.group_id = 0
            markup = types.InlineKeyboardMarkup(row_width=1)
            items = choose_course()
            markup.add(*items)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите курс", reply_markup=markup)
    except Exception as e:
        print(repr(e))


# Call to display step before choosing group (button shown in groups list)
@bot.callback_query_handler(func=lambda call: call.data.startswith('last'))
def callback_faculty_step(call):
    global schedule
    try:
        if call.message:
            schedule.group_id = 0
            markup = types.InlineKeyboardMarkup(row_width=2)
            items = choose_group()
            markup.add(*items)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите группу", reply_markup=markup)
    except Exception as e:
        print(repr(e))


# RUN
bot.infinity_polling(True)
