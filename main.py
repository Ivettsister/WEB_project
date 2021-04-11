from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import os
from maps_api.request import geocoder_request, map_request
from maps_api.geocoder import get_pos, get_bbox, get_country_code, get_city, check_response
from maps_api.static import get_static_map
from weather import get_current_weather, get_forecast_weather

load_dotenv()
keyboard1 = [['Пропустить']]
keyboard2 = [['Показать на карте'], ['Найти ближайшую организацию'], ['Посчитать время на дорогу'], ['Погода'], ['Расписания'],
             ['Вернуться назад']]
keyboard3 = [['Вернуться назад']]
keyboard4 = [['Текущая погода'], ['Прогноз на n дней'], ['Вернуться назад']]
keyboard5 = [['Пешком'], ['На общественном транспорте'], ['На машине']]

inline_maps = InlineKeyboardMarkup([
    [InlineKeyboardButton('Карта', callback_data='map')],
    [InlineKeyboardButton('Спутник', callback_data='sat')],
    [InlineKeyboardButton('Гибрид', callback_data='sat,skl')],
])


def start(update, context):
    update.message.reply_text(
        'Как Вас зовут?', reply_markup=ReplyKeyboardMarkup(keyboard1, one_time_keyboard=False))
    return ENTER_NAME


def enter_name(update, user_data):
    name = update.message.text
    if name != 'Пропустить':
        user_data['username'] = name
    else:
        user_data['username'] = None
        update.message.reply_text('В каком городе Вы находитесь?')
    return ENTER_LOCATION


def enter_location(bot, update, user_data):
    location = update.message.text

    if location != 'Пропустить':
        user_data['location'] = location
    else:
        user_data['location'] = None

    name = ', {}'.format(user_data['username']) if user_data['username'] is not None else ''
    update.message.reply_text('Добро пожаловать{}!'.format(name), reply_markup=ReplyKeyboardMarkup(keyboard2))
    return MAIN_MENU


def main_menu(bot, update, user_data):
    text = update.message.text

    if text == 'Показать на карте':
        update.message.reply_text(
            'Введите адрес места, который хотите увидеть:',
            reply_markup=ReplyKeyboardMarkup(keyboard3)
        )
        pass

    elif text == 'Найти ближайшую организацию':
        update.message.reply_text(
            'Введите название организации, которую хотите найти (аптека/торговый центр):',
            reply_markup=ReplyKeyboardMarkup(keyboard3)
        )
        pass

    elif text == 'Погода':
        update.message.reply_text(
            'Выберите параметры, которые Вы хотите настроить',
            reply_markup=ReplyKeyboardMarkup(keyboard4)
        )
        pass

    elif text == 'Посчитать время на дорогу':
        update.message.reply_text(
            'Выберите параметры, которые Вы хотите настроить',
            reply_markup=ReplyKeyboardMarkup(keyboard5)
        )
        pass
    return MAIN_MENU


def choosing_map_type(bot, update, user_data):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                          text="[​​​​​​​​​​​]({}){}".format(get_static_map(user_data, query.data),
                                                            'Карта для города ' + get_city(
                                                                user_data['current_response'], 'ru-RU')),
                          parse_mode='markdown', reply_markup=inline_maps)


def weather(bot, update, user_data):
    text = update.message.text

    if text == 'Текущая погода':
        city, code = get_city(user_data['current_response']), get_country_code(user_data['current_response'])
        update.message.reply_text(
            get_current_weather(city, code, WEATHER_TOKEN, get_city(user_data['current_response'], 'ru-RU')))

    elif text == 'Прогноз на n дней':
        city, code = get_city(user_data['current_response']), get_country_code(user_data['current_response'])
        update.message.reply_text(
            get_forecast_weather(city, code, WEATHER_TOKEN, get_city(user_data['current_response'], 'ru-RU')))

    elif text == 'Вернуться назад':
        update.message.reply_text('Выберите одну из возможных функций для данного местоположения:',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))

        pass


def stop(bot, update):
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Для того, чтобы начать работу с ботом заново напишите /start')
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


(
    ENTER_NAME, ENTER_LOCATION, MAIN_MENU
) = range(3)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        ENTER_NAME: [MessageHandler(Filters.text, enter_name, pass_user_data=True)],
        MAIN_MENU: [MessageHandler(Filters.text, main_menu, pass_user_data=True)],
        ENTER_LOCATION: [MessageHandler(Filters.text, enter_location, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    main()
