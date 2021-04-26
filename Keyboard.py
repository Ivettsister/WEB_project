from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

keyboard1 = [['Пропустить']]
keyboard2 = [['Показать на карте'], ['Найти ближайшую организацию'], ['Посчитать время на дорогу'],
             ['Погода'], ['Расписания'],
             ['Вернуться назад']]
keyboard3 = [['Вернуться назад']]
keyboard4 = [['Текущая погода'], ['Прогноз на 6 дней'], ['Вернуться назад']]
keyboard5 = [['Пешком'], ['На общественном транспорте'], ['На машине']]
keyboard6 = [['Вернуться назад'], ['Мое расположение']]
keyboard7 = [['Вернуться назад'], ['Мое расположение']]
keyboard_back = [['Вернуться назад']]
keyboard_number_of_companies = [['Вернуться назад'], ['Пропустить']]
keyboard_get_result = [['Получить результат']]
keyboard_all_stations = [['Вернуться назад']]
inline_maps = InlineKeyboardMarkup([
    [InlineKeyboardButton('Карта', callback_data='map')],
    [InlineKeyboardButton('Спутник', callback_data='sat')],
    [InlineKeyboardButton('Гибрид', callback_data='sat,skl')],
])
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[['Пропустить']])
