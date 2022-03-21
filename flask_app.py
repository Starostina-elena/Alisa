import os

from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# картинки для городов
cities = {
    'москва': ['1540737/27d960d237be74e86a2c',
               '1030494/b54dbb792e449b6fc915'],
    'нью-йорк': ['213044/5c42a65a5afb1929fe79',
                 '213044/a2f983645ae4c3c915b6'],
    'париж': ['1521359/b1d803fd4430fa2fb145',
              '213044/b09a2e78c06e2a67c7b9']
}

# имена пользователей
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info(f'Response: {response!r}')

    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'

        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    if sessionStorage[user_id]['first_name'] is None:

        first_name = get_first_name(req)

        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = 'Приятно познакомиться, ' \
                                      + first_name.title() \
                                      + '. Я - Алиса. Какой город хочешь увидеть?'

            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]

    # пользователь говорит о городе, который хочет увидеть
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = 'Я угадал!'
        else:
            res['response']['text'] = \
                'Первый раз слышу об этом городе. Попробуй еще разок!'


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
