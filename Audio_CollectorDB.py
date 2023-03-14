import yaml

# Common db YAML file
db_yaml = {
   'id': [],
   'command_1_1': [],
   'command_1_2': [],
   'command_1_3': [],

   'command_2_1': [],
   'command_2_2': [],
   'command_2_3': [],

   'command_3_1': [],
   'command_3_2': [],
   'command_3_3': [],

   'command_4_1': [],
   'command_4_2': [],
   'command_4_3': [],

   'command_5_1': [],
   'command_5_2': [],
   'command_5_3': [],

   'command_6_1': [],
   'command_6_2': [],
   'command_6_3': [],

   'command_7_1': [],
   'command_7_2': [],
   'command_7_3': [],

   'command_8_1': [],
   'command_8_2': [],
   'command_8_3': [],

   'command_9_1': [],
   'command_9_2': [],
   'command_9_3': [],

   'command_10_1': [],
   'command_10_2': [],
   'command_10_3': [],

   'command_11_1': [],
   'command_11_2': [],
   'command_11_3': [],

   'command_12_1': [],
   'command_12_2': [],
   'command_12_3': [],

   'command_13_1': [],
   'command_13_2': [],
   'command_13_3': [],

   'command_14_1': [],
   'command_14_2': [],
   'command_14_3': [],

   'command_15_1': [],
   'command_15_2': [],
   'command_15_3': [],

   'command_16_1': [],
   'command_16_2': [],
   'command_16_3': [],

   'command_17_1': [],
   'command_17_2': [],
   'command_17_3': [],

   'command_18_1': [],
   'command_18_2': [],
   'command_18_3': [],

   'is_ready': [],
}

with open('audio_db.yaml', 'w') as f:
    yaml.dump(db_yaml, f)

with open('audio_db.yaml') as f:
    print(f.read())

# Commands YAML file
commands_list = ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить']
commands_yaml = {
    'iter_1': ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить'],
    'iter_2': ['Старт', 'Стоп', 'Домой', 'Найти', 'Захватить', 'Поднять', 'Опустить', 'Двигаться', 'Остановиться', 'Влево', 'Вправо',
                 'Вверх', 'Вниз', 'Открыть', 'Закрыть', 'Сменить', 'Сохранить', 'Загрузить'],
    'iter_3': [0, 12, 2323]
}

with open('audio_commands.yaml', 'w') as f:
    yaml.dump(commands_yaml, f)

with open('audio_commands.yaml') as f:
    print(f.read())

user_states_to_yaml = {
    0 : 'cond'    
}
with open('user_states.yaml', 'w') as f:
    yaml.dump(user_states_to_yaml, f)
