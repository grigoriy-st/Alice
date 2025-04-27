from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

city_geo_info = {
    'москва': {
        'country': 'Россия',
        'coordinates': [55.7558, 37.6173]
    },
    'нью-йорк': {
        'country': 'США',
        'coordinates': [40.7128, -74.0060]
    },
    'париж': {
        'country': 'Франция',
        'coordinates': [48.8566, 2.3522]
    }
}

cities = {
    'москва': ['1652229/a4629d09fcc37c13bca7',
               '1030494/d76924726c2bbace0a9e'],
    'нью-йорк': ['14236656/4428ffdd86811a8ae6f1',
                 '1652229/65fe6a05702c79bed750'],
    'париж': ["1652229/6fc396e8daaf170ce1f7",
              '1652229/65fe6a05702c79bed750']
}

sessionStorage = {}

def get_geo_info(city_name, type_info):
    city_data = city_geo_info.get(city_name.lower())
    if not city_data:
        return None
    
    return city_data.get(type_info)

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
    return jsonify(response)

def handle_dialog(res, req):
    user_id = req['session']['user_id']

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
            res['response']['text'] = 'Приятно познакомиться, ' + first_name.title() + '. Я - Алиса. Какой город хочешь увидеть?'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = f'Я угадал! Страна: {get_geo_info(city, "country")}'
        else:
            res['response']['text'] = 'Первый раз слышу об этом городе. Попробуй еще разок!'

def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)

def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)

if __name__ == '__main__':
    app.run()