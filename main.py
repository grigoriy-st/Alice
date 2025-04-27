from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

animal_phrases = {
    'слон': {
        'куплю': 'Хорошо, вот реквизиты для перевода слона!',
        'зачем': 'Чтобы было чем гордиться!',
        'не поместится': 'Зато соседи завидовать будут!',
        'нет денег': 'Продай ноутбук и купи слона!',
        'не нужен': 'Ты просто не понимаешь своего счастья!',
        'что ест': 'Всё! Особенно тех, кто не покупает слонов!',
        'где держать': 'В шкафу! Или в ванной...',
        'дорого': 'Зато потом скажешь: "У меня есть слон!"',
        'передумал': 'Слоны не любят нытиков!',
        'ладно': 'Вот и умница! Теперь купи кролика!',
        'нет': [
            'Нет — это всего лишь слово! Купи слона!',
            'Слоны не любят слово "нет"!',
            'А если слон скажет тебе "нет"?',
            'Нет? Значит, купишь двух слонов!'
        ]
    },
    'кролик': {
        'куплю': 'Отлично, вот реквизиты для кролика!',
        'зачем': 'Чтобы было с кем пить чай!',
        'не поместится': 'Он же маленький!',
        'нет денег': 'Продай телефон и купи кролика!',
        'не нужен': 'Как ты будешь жить без кролика?',
        'что ест': 'Морковку и твои сомнения!',
        'где держать': 'В клетке или в тапке!',
        'дорого': 'Зато пушистый!',
        'передумал': 'Кролики обижаются!',
        'ладно': 'Молодец! Теперь купи слона!',
        'нет': [
            'Нет? А кто будет есть морковку?',
            'Кролики не принимают "нет"!',
            'Скажешь нет — купишь двух!'
        ]
    }
}

available_phrases = ['куплю', 'покупаю', 'хорошо', 'ладно', 'я куплю', 'я покупаю']

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

    return jsonify(response)

def handle_dialog(res, req):
    user_id = req['session']['user_id']
    
    if req['session']['new']:
        res['response']['text'] = 'Привет! Купи слона!'
        sessionStorage[user_id] = {
            'current_animal': 'слон',
            'next_animal': 'кролик'
        }
        return
    
    user_text = req['request']['original_utterance'].lower()
    current_animal = sessionStorage[user_id]['current_animal']
    phrases = animal_phrases[current_animal]
    
    if user_phrase_in_available_phrases(user_text):
        res['response']['text'] = phrases['куплю']
        next_animal = 'слон' if current_animal == 'кролик' else 'кролик'
        res['response']['text'] += f' Теперь купи {next_animal}!'
        sessionStorage[user_id] = {
            'current_animal': next_animal,
            'next_animal': 'слон' if next_animal == 'кролик' else 'кролик'
        }
    else:
        response_text = None
        for phrase in phrases:
            if phrase in user_text:
                if isinstance(phrases[phrase], list):
                    response_text = random.choice(phrases[phrase])
                else:
                    response_text = phrases[phrase]
                break
        
        if not response_text:
            if "нет" in user_text:
                response_text = random.choice(phrases["нет"])
            else:
                response_text = f"Всё равно купи {current_animal}!"
        
        res['response']['text'] = response_text
    
    res['response']['buttons'] = [
        {'title': phrase.capitalize(), 'hide': True} 
        for phrase in random.sample(list(phrases.keys()), min(5, len(phrases)))
    ]

def user_phrase_in_available_phrases(user_phrase):
    for phrase in available_phrases:
        if phrase in user_phrase:
            return True
    return False

if __name__ == '__main__':
    app.run()