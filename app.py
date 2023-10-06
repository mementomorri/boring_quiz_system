import os

from flask import Flask, session, request, redirect, render_template, url_for, Response
from http import HTTPStatus
from db_crud import get_question_after
from dotenv import load_dotenv

import utility_functions
from object_types import template

load_dotenv()
folder = os.getcwd()  # запомнили текущую рабочую папку и создаем объект app
app = Flask(__name__, template_folder=folder+"/template", static_folder=folder+"/static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Получаем ключ шифрованмя из переменной среды


@app.route('/', methods=["GET", "POST"])
def index() -> template | Response | HTTPStatus:
    """ Корневая страница:
    - если пришли с запросом GET, то предаставляем список викторин;
    - если POST - то фиксируем id викторины и перенаправляем на вопросы """
    if request.method == 'GET':
        utility_functions.start_quiz(-1)  # сбрасываем id викторины и показываем форму выбора
        return utility_functions.quiz_form()
    elif request.method == 'POST':
        quest_id = request.form.get('quiz')  # фиксируем выбранный номер викторины в переданных данных
        utility_functions.start_quiz(int(quest_id))
        return redirect(url_for('test'))
    else:
        return HTTPStatus.BAD_REQUEST


@app.route('/test', methods=["GET", "POST"])
def test() -> template | Response:
    """ Возвращает шаблон страницуы вопроса, шаблон собирается в зависимости от выбранной викторины """
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':  # обновляем текущее состояние в случае получения данных
            utility_functions.save_answers()
        next_question = get_question_after(session['last_question'], session['quiz'])
        if next_question is None or len(next_question) == 0:  # Проверяем остались ли вопросы
            return redirect(url_for('result'))
        else:
            return utility_functions.question_form(next_question)


@app.route('/result', methods=["GET"])
def result() -> template | Response:
    """ Возвращает результат викторины в завимости от сохраненных в сессию ответов """
    if 'answers' in session:
        html = render_template('result.html', right=session['answers'], total=session['total'])
        utility_functions.end_quiz()  # Сперва собираем форму с результатом, а затем завершаем викторину
        return html
    else:
        return redirect(url_for('index'))


# Точка входа
if __name__ == "__main__":
    app.run(
            host='0.0.0.0',
            port=8080)
