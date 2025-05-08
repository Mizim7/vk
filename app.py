from flask import Flask, render_template
import vk_api
from datetime import datetime

app = Flask(__name__)

LOGIN = '89005727070'
PASSWORD = 'PoWeR07042007$'
GROUP_ID_DEFAULT = 230405791

vk_session = None
vk = None


def login_to_vk():
    global vk_session, vk
    try:
        vk_session = vk_api.VkApi(
            login=LOGIN,
            password=PASSWORD,
            auth_handler=auth_handler,
            captcha_handler=captcha_handler
        )
        vk_session.auth(token_only=False)
        vk = vk_session.get_api()
        print("Авторизация прошла успешно")
    except Exception as e:
        print("Ошибка авторизации:", e)


def auth_handler():
    key = input("Введите код двухфакторной аутентификации: ")
    remember_device = True
    return key, remember_device


def captcha_handler(captcha):
    key = input(f"Введите код с капчи ({captcha.get_url()}): ").strip()
    return captcha.try_again(key)


def get_vk_stats(group_id):
    if not vk:
        return []

    try:
        response = vk.stats.get(group_id=group_id, fields='reach')
        print("Ответ от VK API:", response)
        items = response[:10]
        stats_list = []
        for item in items:
            period_unix = item['period_from'] / 1000
            period_date = datetime.fromtimestamp(period_unix).strftime('%Y-%m-%d')
            reach = item.get('reach', {})
            stat = {
                'date': period_date,
                'likes': reach.get('likes', 0),
                'comments': reach.get('comments', 0),
                'subscribed': reach.get('reach_subscribers', 0),
                'age_groups': {age['name']: age['value'] for age in reach.get('age', [])},
                'cities': ', '.join(set(city['name'] for city in reach.get('cities', [])))
            }
            stats_list.append(stat)

        return stats_list
    except Exception as e:
        print("Ошибка получения данных:", e)
        return []


@app.route('/')
def index():
    return "Введите ID группы в адресной строке как: /vk_stat/123456789"


@app.route('/vk_stat/<int:group_id>')
def show_stats(group_id):
    stats = get_vk_stats(group_id)
    return render_template('stats.html', group_id=group_id, stats=stats)


if __name__ == '__main__':
    login_to_vk()
    app.run(debug=True)
