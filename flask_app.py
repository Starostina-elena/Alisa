import os

from flask import Flask, request

import logging
import json

from geo import get_country, get_distance, get_coordinates

app = Flask(__name__)


# словарь с подсказками (текст на кнопках)
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


logging.basicConfig(level=logging.INFO)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

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
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Я могу показать город или сказать расстояние между городами!'
    # else:
    #     city = get_city(req)
    #     if city in cities:
    #         res['response']['card'] = {}
    #         res['response']['card']['type'] = 'BigImage'
    #         res['response']['card']['title'] = 'Этот город я знаю.'
    #         res['response']['card']['image_id'] = random.choice(cities[city])
    #         res['response']['text'] = 'Я угадал!'
    #     # если не нашел, то отвечает пользователю
    #     # 'Первый раз слышу об этом городе.'
    #     else:
    #         res['response']['text'] = \
    #             'Первый раз слышу об этом городе. Попробуй еще разок!'
    else:
        cities = get_cities(req)
        if not cities:
            res['response']['text'] = 'Ты не написал название ни одного города!'
        elif len(cities) == 1:
            res['response']['text'] = 'Этот город в стране - ' + \
                                      get_country(cities[0])
        elif len(cities) == 2:
            distance = get_distance(get_coordinates(
                cities[0]), get_coordinates(cities[1]))
            res['response']['text'] = 'Расстояние между этими городами: ' + \
                                      str(round(distance)) + ' км.'
        else:
            res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
