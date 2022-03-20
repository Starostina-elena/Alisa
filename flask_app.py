import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# словарь с подсказками (текст на кнопках)
sessionStorage = {}

animal = dict()


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    # ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    print(request.json['session']['user_id'])

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.

        animal[req['session'][user_id]] = 'слон'

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу",
                "Не буду",
                "Отстань!",
            ]
        }

        # текст ответа
        res['response']['text'] = f'Привет! Купи {animal[req["session"]["user_id"]]}а!'

        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)

        return

    # пользователь не новый
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = f'{animal[req["session"]["user_id"]].capitalize()}а можно найти на Яндекс.Маркете!'

        if animal[req["session"]["user_id"]] == 'слон':
            animal[req["session"]["user_id"]] = 'кролик'

            sessionStorage[user_id] = {
                'suggests': [
                    "Не хочу",
                    "Не буду",
                    "Отстань!",
                ]
            }

            # текст ответа
            res['response']['text'] = f'Снова привет! Купи {animal[req["session"]["user_id"]]}а!'

            # Получим подсказки
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['end_session'] = True
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal[req['session']['user_id']]}а!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animal[user_id]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
