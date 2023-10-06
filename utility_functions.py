from random import shuffle
from flask import session, request, render_template

from db_crud import get_all_quiz, check_answer
from object_types import Question, template


def start_quiz(quiz_id: int | None) -> None:
    """ Создаёт нужные значения в сессии соединения пользователя.
    :param quiz_id: int - номер выбранной викторины.
    """
    if quiz_id is not None:
        session['quiz'] = quiz_id
    else:
        session['quiz'] = 1
    session['last_question'] = 0
    session['answers'] = 0
    session['total'] = 0


def end_quiz() -> None:
    """ Подчищает сессию сединения пользователя, чтобы иметь возможность
        проходить викторины независимо от предыдущих результатов. """
    session.clear()


def quiz_form() -> template:
    """ Получает список викторин из БД и возвращаем форму с выпадающим списком.
     :return: template: str - собранный шаблон."""
    q_list = get_all_quiz()
    return render_template('index.html', q_list=q_list)


def save_answers() -> None:
    """ Получает данные из формы, проверяет корректность, записывает результат проверки в сессию"""
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    session['last_question'] = quest_id
    session['total'] += 1  # увеличиваем счетчик вопросов
    if check_answer(int(quest_id), answer):  # проверяем, совпадает ли ответ с верным для этого вопроса, по его id
        session['answers'] += 1


def question_form(question: Question) -> template:
    """
    :param question: Question - вопрос который мы хотим сформировать;
    :return: template: str - собранный шаблон.
    получает строку из базы данных, соответствующую вопросу, возвращает собранный шаблон с формой,
    question - результат работы get_question_after, где поля объекта поля:
    [0] - номер вопроса в викторине,
    [1] - текст вопроса,
    [2] - правильный ответ, [3],[4],[5] - неверные ответы"
    """
    answers_list = [
        question.answer, question.wrong1, question.wrong2, question.wrong3
    ]
    shuffle(answers_list)  # перемешиваем ответы, передаём в шаблон и возвращаем форму
    return render_template('question.html', question=question.question, quest_id=question.id, answers_list=answers_list)
