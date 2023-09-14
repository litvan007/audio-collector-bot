#!/usr/bin/python

import yaml
import random
from telebot import types
from telebot.async_telebot import AsyncTeleBot

import asyncio
import requests
from bs4 import BeautifulSoup

import os
from scipy.io import wavfile

android_root = "./android_inst"

bot = AsyncTeleBot('6060192876:AAE6615iBZ-hrwvTEUQanhoDD-LPHMnH_FI')

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_message(599202079, text = f'Пользователь {message.from_user.username if message.from_user.username is not None else "Empty"} Начал работу с ботом', 
                            parse_mode="HTML") 

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Android", callback_data="Android")
    btn2 = types.InlineKeyboardButton("IOS", callback_data="IOS")

    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, 
    '''Приветствую! Вы участвуете в процессе сбора аудиоданных для моей курсовой работы "Создание системы голосового управления для механического манипулятора".
Собранные аудиозаписи будут использоваться в обучении нейросети по распознаванию голосовых команд. И, в дальнейшем разработанная система голосового управления будет интегрирована в рабочий прототип манипулятора на МКС.
Чтобы приступить, выберите тип вашего устройства
    ''', reply_markup=markup
    )
    
    await bot.send_message(message.chat.id, text='В новой версии бота теперь доступны анекдоты после нескольких отправленных записей'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'Android' or call.data == 'IOS')
async def callback_sys(call):
    if call.data == "Android":
        await bot.send_message(call.message.chat.id, 
        '''Для начала необходимо установить программу на ваше устройство для записи аудио (использовать только это метод) \
        \nhttps://play.google.com/store/apps/details?id=com.raytechnoto.glab.voicerecorder
        ''')

        # await asyncio.sleep(10)
        await bot.send_message(call.message.chat.id, 
        '''Затем выставите соответствующие настройки:
        ''')
        lst_files = os.listdir(android_root)
        media = [types.InputMediaPhoto(open(f'./{android_root}/{photo}', 'rb')) for photo in lst_files]
        await bot.send_media_group(call.message.chat.id, media=media)

    if call.data == "IOS":
        await bot.send_message(call.message.chat.id, 
        '''Для начала необходимо установить программу на ваше устройство для записи аудио (использовать только это метод) \
        \nhttps://apps.apple.com/ru/app/voice-record-pro/id546983235?l=en    
        ''')

        # await asyncio.sleep(10)
        await bot.send_message(call.message.chat.id, 
        '''Затем нажмите на кнопку REC и выставите настройки как на фото: 
        ''')

        with open('IOS_inst.jpg', 'rb') as f:
            photo = f.read()
            await bot.send_photo(call.from_user.id, photo, caption='Настройки')

    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
    markup_ready = types.InlineKeyboardMarkup()

    btn = types.InlineKeyboardButton("Начинаем", callback_data='Ready')
    markup_ready.add(btn)
    
    await asyncio.sleep(10)
    await bot.send_message(call.message.chat.id, 
        ''' Вы готовы приступить к записи вашего голоса? ''', reply_markup=markup_ready)

@bot.callback_query_handler(func=lambda call: call.data == 'Ready')
async def user_recording(call):
    users_dir = [f for f in os.listdir() if os.path.isdir(f)]
    if f'user_{call.from_user.id}' not in users_dir:
        path = f"./user_{call.from_user.id}"
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
        commands_data_create(path)
        with open(f'user_{call.from_user.id}/username', 'w') as f:
            f.write(call.from_user.username if call.from_user.username is not None else 'Empty')
        with open(f'user_{call.from_user.id}/cond', 'w') as f:
            f.write('54\n') # TODO
            f.write('waiting_for_phrase')
    
    await bot.send_message(599202079, text = f'Пользователь {call.from_user.username if call.from_user.username is not None else "Empty"} зарагестрировался', 
                            parse_mode="HTML") 

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_button = types.KeyboardButton("Получить фразу")
    keyboard.add(get_button)
    await bot.send_message(call.message.chat.id, text = '''Запись голоса происходит <b>исключительно через скаченное приложение</b>
        ''', parse_mode="HTML", reply_markup=keyboard)

@bot.message_handler(content_types=['text'], regexp=r"Получить фразу")
async def get_phrase(message):
    try:
        state = None
        with open(f'user_{message.from_user.id}/cond', 'r') as f:
            state = f.readlines()

        if state[1] == 'end':
            await bot.send_message(message.chat.id, text='Вы отправили все записи. Если у вас остались какие-либо сомнения, то напишите @Ivanhoe_w', 
                                        parse_mode="HTML")

        elif state[1] != 'waiting_for_phrase' and state[1] != 'end':
            await bot.send_message(message.chat.id, text='Вы не отправили запись предыдущей команды', parse_mode="HTML")

        elif state[1] == 'waiting_for_phrase':
            commands_list = {}
            with open(f"./user_{message.from_user.id}/audio_commands.yaml", 'r') as f:
                commands_list = yaml.safe_load(f.read())

            state[0] = len(commands_list['iter_1']) + len(commands_list['iter_2']) + len(commands_list['iter_3'])
            if len(commands_list['iter_1']) == 0 and len(commands_list['iter_2']) == 0 and len(commands_list['iter_3']) == 0:
                await bot.send_message(message.chat.id, text='Вы отправили все записи. Если у вас остались какие-либо сомнения, то напишите @Ivanhoe_w', 
                                        parse_mode="HTML")
                state[1] = 'end'

            else:
                cond = 0
                if len(commands_list['iter_1']) != 0:
                    n_1 = len(commands_list['iter_1'])
                    index = random.randint(1, n_1)
                    curr_command = commands_list['iter_1'].pop(index-1)
                    cond = 1

                elif len(commands_list['iter_2']) != 0:
                    n_2 = len(commands_list['iter_2'])
                    index = random.randint(1, n_2)
                    curr_command = commands_list['iter_2'].pop(index-1)
                    cond = 2

                elif len(commands_list['iter_3']) != 0:
                    n_3 = len(commands_list['iter_3'])
                    index = random.randint(1, n_3)
                    curr_command = commands_list['iter_3'].pop(index-1)
                    cond = 3

                with open(f"./user_{message.from_user.id}/audio_commands.yaml", 'w') as f:
                    yaml.safe_dump(commands_list, f)

                await bot.send_message(message.chat.id, text='Запишите команду:', parse_mode="HTML")                    
                await bot.send_message(message.chat.id, text=f'<b>{curr_command}</b>', parse_mode="HTML")                    
                await bot.send_message(message.chat.id, text='Отправьте аудиозапись <b>файлом</b> или <b>аудио</b>', parse_mode="HTML")
                state[1] = f'{curr_command}_{index}_{cond}'

            with open(f'user_{message.from_user.id}/cond', 'w') as f:
                f.write(str(state[0])+'\n')
                f.write(state[1])

    except FileNotFoundError:
        await bot.send_message(message.chat.id, text='Для начала прочитайте до конца инструкцию <b>/help</b>', parse_mode="HTML")

async def get_joke():
    joke_html = requests.get('https://nekdo.ru/random/').text
    joke_text = BeautifulSoup(joke_html, 'lxml').find('div', class_='text').get_text()

    return joke_text

@bot.message_handler(content_types=['document', 'audio'])
async def audio_handler(message):
    try:
        state = None
        with open(f'user_{message.from_user.id}/cond', 'r') as f:
            state = f.readlines()

        if state[1] != 'waiting_for_phrase' and state[1] != 'end':
            file_type = message.document.mime_type if message.content_type == 'document' else message.audio.mime_type
#print(file_type)
            if file_type.split('/')[-1] != 'x-wav':
                await bot.send_message(message.chat.id, text="Файл должен быть в формате <b>wav</b>\nПройдите инcтрукцию /help", parse_mode="HTML")
            else:
                file_info = (await bot.get_file(message.document.file_id if message.content_type == 'document' else message.audio.file_id))
                downloaded_file = (await bot.download_file(file_info.file_path))
                with open(f'./user_{message.from_user.id}/{state[1]}.wav', 'wb') as new_file:
                        new_file.write(downloaded_file)
                sr, audio = wavfile.read(f'./user_{message.from_user.id}/{state[1]}.wav')
                # print(sr, len(audio)/sr)
                if sr != 16000:
                    await bot.send_message(message.chat.id, text=f"Параметр <b>Sample Rate</b> был выставлен неверно. Необходимое значение <b>16000</b>", parse_mode="HTML")
                elif len(audio)/sr >= 6:
                    await bot.send_message(message.chat.id, text=f"Ваша запись слишком большая. Нeобходима длина менее 5 секунд", parse_mode="HTML")
                else:
                    state[0] = str(int(state[0].split('\n')[0]) - 1) + '\n'
                    await bot.send_message(599202079, text = f'''Пользователь {message.from_user.username if message.from_user.username is not None else "Empty"} отправил слово {state[1]}
Ему осталось {state[0]}''')
                    with open(f'user_{message.from_user.id}/cond', 'w') as f:
                        if int(state[0]) == 0:
                          state[1] = 'end'
                        else:
                          state[1] = 'waiting_for_phrase'
                        f.write(state[0])
                        f.write(state[1])
                    await bot.send_message(message.chat.id, text=f"Запись получена. {54-int(state[0])}/54", parse_mode="HTML") # TODO

                    if int(state[0]) % random.randint(3, 5) == 0:
                        text = await get_joke()
                        await bot.send_message(599202079, text = f'Пользователь {message.from_user.username if message.from_user.username is not None else "Empty"} получил анекдот: {text}', 
                            parse_mode="HTML")
                        await bot.send_message(message.chat.id, 'Отлично! Если бы мой бот мог аплодировать, он бы это сделал! Вы заслужили анекдот')
                        await bot.send_message(message.chat.id, text)

        elif state[1] == 'waiting_for_phrase':
            await bot.send_message(message.chat.id, text="Для начала получите фразу", parse_mode="HTML")

        if state[1] == 'end':
            await bot.send_message(message.chat.id, text='Поздравляю! Вы отправили все записи. Если у вас остались какие-либо сомнения, то напишите @Ivanhoe_w', 
                                        parse_mode="HTML")
    except FileNotFoundError:
        await bot.send_message(message.chat.id, text="Для начала прочитайте инструкцию /help", parse_mode="HTML")

@bot.message_handler(commands=['help'])
async def send_welcome(message):
    await bot.send_message(599202079, text = f'Пользователь {message.from_user.username if message.from_user.username is not None else "Empty"} запутался', 
                            parse_mode="HTML") 
    await bot.send_message(message.chat.id, 
    ''' 1) Если вы не нажимали кнопку <b>Начинаем</b>, то снова введите /start.
2) Если вы случайно удалили чат, то необходимо снова ввести /start, а затем нажать кнопку <b>Начинаем</b>.
3) Чтобы вспомнить какую фразу вам надо записать введите /status.
4) Если вы отправляли некорректный файл, пожалуйста, выставите правильные настройки в вашем приложении для записи аудио. 
5) Если вы получили в процессе использования рекомендацию выбрать /help, то скорее всего вы нарушаете порядок работы с ботом, поэтому рекомендую удалить этот чат и начать работу с начала. 
6) Если вы не понимаете зачем это нужно, или что будет с вашими персональными данными, или вы по любым другим вопросам, то просто напишите @Ivanhoe_w.
    ''', parse_mode='HTML'
    )

@bot.message_handler(commands=['status'])
async def send_welcome(message):
    try:
        with open(f'user_{message.from_user.id}/cond', 'r') as f:
            cnt, word = f.readlines()
            await bot.send_message(message.chat.id, f"Текущая фраза <b>{word.split('_')[0] if word != 'waiting_for_phrase' else 'еще не получена'}</b>\nЗаписано {54-int(cnt)}/54", parse_mode='HTML')
    except FileNotFoundError:
        await bot.send_message(message.chat.id, f"Чтобы узнать сколько вам нужно сделать аудиозаписей, прочитайте до конца инструкцию")


def commands_data_create(path):
    commands_yaml = {
    'iter_1': ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить'],
    'iter_2': ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить'],
    'iter_3': ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить'],
    }
    # commands_yaml = {
    # 'iter_1': ['Старт', 'Стоп'],
    # 'iter_2': ['Старт', 'Стоп'],
    # 'iter_3': ['Старт', 'Стоп'],
    # }
    with open(f'{path}/audio_commands.yaml', 'w') as f:
        yaml.dump(commands_yaml, f)

import asyncio
asyncio.run(bot.polling(non_stop=True, request_timeout=90))
