import sqlite3
import os
from sqlite3 import Connection, Cursor
from random import choice
from dotenv import load_dotenv

from object_types import Question, Quiz
import conf
load_dotenv()

conn: Connection
cursor: Cursor


def open_db_connection() -> None:
    """ Открывает соединение с БД """
    global conn, cursor
    conn = sqlite3.connect(os.getenv('DB_RELATIVE_PATH'))  # Получаем путь к БД из переменной среды
    cursor = conn.cursor()


def close_db_connection() -> None:
    """ Закрывает соединение с БД """
    global conn, cursor
    if conn is not None and cursor is not None:
        cursor.close()
        conn.close()


def do_query(query: str) -> None:
    """ Выполняет запрос указанный в качестве аргумента query """
    global conn, cursor
    if conn is not None and cursor is not None:
        cursor.execute(query)
        conn.commit()


def clear_db() -> None:
    """ Удаляет целевые таблицы из БД, чтобы избежать конфликтации """
    open_db_connection()
    for table_name in conf.target_tables:
        do_query("DROP TABLE IF EXISTS "+table_name)
    close_db_connection()


def create_target_tables() -> None:
    """ Создает целевые таблицы """
    open_db_connection()
    cursor.execute('''PRAGMA foreign_keys=on''')

    do_query('''CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY, 
            name VARCHAR)'''
             )
    do_query('''CREATE TABLE IF NOT EXISTS question (
                id INTEGER PRIMARY KEY, 
                question VARCHAR, 
                answer VARCHAR, 
                wrong1 VARCHAR, 
                wrong2 VARCHAR, 
                wrong3 VARCHAR)'''
             )
    do_query('''CREATE TABLE IF NOT EXISTS quiz_content (
                id INTEGER PRIMARY KEY,
                quiz_id INTEGER,
                question_id INTEGER,
                FOREIGN KEY (quiz_id) REFERENCES quiz (id),
                FOREIGN KEY (question_id) REFERENCES question (id) )'''
             )
    close_db_connection()


def get_table(table_name: str) -> list[tuple[str]]:
    """ Возвращает содержимое таблицы указанной в аргументе table_name
    :param table_name: str - имя таблицы используемое для поиска про БД;
    :return: list - список кортежей из содержимого таблицы.
    """
    query = 'SELECT * FROM ' + table_name
    open_db_connection()
    cursor.execute(query)
    result = cursor.fetchall()
    close_db_connection()
    return result


def show_tables() -> None:
    """ Выводит в консоль содержимое всез целевых таблиц.
        Функция для дебаггинга."""
    for table_name in conf.target_tables:
        print(get_table(table_name))


def add_test_questions() -> None:
    """ Заполняет таблицу quiestion примерами вопросов для вывода на тестовой викторине """
    open_db_connection()
    cursor.executemany('''INSERT INTO question (question, answer, wrong1, wrong2, wrong3) VALUES (?,?,?,?,?)''',
                       conf.questions)
    conn.commit()
    close_db_connection()


def add_test_quiz() -> None:
    """ Заполняет таблицу quiz тестовыми викторинами для вывода на викторине"""
    open_db_connection()
    cursor.executemany('''INSERT INTO quiz (name) VALUES (?)''', conf.quiz_names)
    conn.commit()
    close_db_connection()


def add_links_interactively() -> None:
    """ Интерактивно добавляет связи между вопросами в таблице question и викторинами в таблице quiz """
    open_db_connection()
    cursor.execute('''PRAGMA foreign_keys=on''')
    query = "INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)"
    answer = input("Добавить связь (y / n)?")
    while answer != 'n':
        quiz_id = int(input("id викторины: "))
        question_id = int(input("id вопроса: "))
        cursor.execute(query, [quiz_id, question_id])
        conn.commit()
        answer = input("Добавить связь (y / n)?")
    close_db_connection()


def add_link(id_question: int, id_quiz: int) -> None:
    """ Добавляет связь между вопросом по id_question в таблице question
        и викториной по id_quiz в таблице quiz
        :param id_question: int - номер вопроса для связывания с викториной;
        :param id_quiz: int - номер викторины для связывания с вопросом."""
    open_db_connection()
    cursor.execute('''PRAGMA foreign_keys=on''')
    query = "INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)"
    cursor.execute(query, [id_quiz, id_question])
    conn.commit()
    close_db_connection()


def get_quiz_lenght(id_quiz: int) -> int:
    """
    Возвращает количество вопросов в викторине.
    Вспомогательная функция для отображения количества вопросов на форме с вопросом.
    :param id_quiz: int - номер викторины для идентификации викторины в БД;
    :return: int - количество вопросов в викторине.
    """
    open_db_connection()
    query = '''
    SELECT question_id
    FROM quiz_content 
    WHERE quiz_content.quiz_id == ?
     '''
    cursor.execute(query, [id_quiz])
    result = cursor.fetchall()
    close_db_connection()
    return len(result) if result is not None else 0


def get_question_after(last_question_id: int = 0, id_quiz: int = 1) -> Question | None:
    """ Возвращает следующий вопрос после вопроса с переданным id,
    для первого вопроса передается значение по умолчанию
    :param last_question_id: int - номер предыдущего вопроса;
    :param id_quiz: int - номер викторины;
    :return: Question - если ещё остались вопросы или None - если вопосов больше не осталось."""
    open_db_connection()
    query = '''
    SELECT quiz_content.id, question.question, question.answer, question.wrong1, question.wrong2, question.wrong3
    FROM question, quiz_content 
    WHERE quiz_content.question_id == question.id
    AND quiz_content.id > ? AND quiz_content.quiz_id == ? 
    ORDER BY quiz_content.id '''
    cursor.execute(query, [last_question_id, id_quiz])

    result = cursor.fetchone()
    close_db_connection()
    if result is not None:
        return Question(result[0], result[1], result[2], result[3], result[4], result[5])
    else:
        return result


def get_all_quiz() -> list[Quiz]:
    """ возвращает список викторин в формате (id, name),
    можно брать только викторины, в которых есть вопросы """
    query = 'SELECT * FROM quiz ORDER BY id'
    open_db_connection()
    cursor.execute(query)
    result = cursor.fetchall()
    close_db_connection()
    return result


def check_answer(id_question: int, ans_text: str) -> bool:
    """ Сверяет выбранный ответ с правильным, указанным в вопросе.
        Возвращает логическую велечину.
        :param id_question: int - номер вопроса;
        :param ans_text: int - текст правильного ответа;
        :return: bool - результат проверки.
    """
    query = '''
            SELECT question.answer 
            FROM quiz_content, question 
            WHERE quiz_content.id = ? 
            AND quiz_content.question_id = question.id
        '''
    open_db_connection()
    cursor.execute(query, str(id_question))
    result = cursor.fetchone()
    close_db_connection()
    if result is not None:
        if result[0] == ans_text:
            return True  # Ответ совпал с вернум
    else:
        return False  # Ответ не совпал с верным


def get_quiz_count() -> tuple[int]:
    """ Возвращает максимальное значение id в таблице quiz_content """
    query = 'SELECT MAX(quiz_id) FROM quiz_content'
    open_db_connection()
    cursor.execute(query)
    result = cursor.fetchone()
    close_db_connection()
    return result


def get_random_quiz_id() -> int:
    """ Возвращает id случайной викторины """
    query = 'SELECT quiz_id FROM quiz_content'
    open_db_connection()
    cursor.execute(query)
    ids = cursor.fetchall()
    rand_id = choice(ids)
    close_db_connection()
    return rand_id


def randomly_distribute_questions() -> None:
    """ Случайным образом распределяет вопросы по викторинам """
    questions_id_list = get_table('question')
    quiz_id_list = get_table('quiz')
    for _ in range(len(questions_id_list)):
        current_question = choice(questions_id_list)
        add_link(int(current_question[0]), int(choice(quiz_id_list)[0]))
        questions_id_list.remove(current_question)


def main() -> None:
    """ Отчищает БД от таблиц, которые потенциально могут конфликтовать
        с целевыми таблицами проекта и создает новые, случайным образом перемешивая вопросы между викторинами"""
    clear_db()
    create_target_tables()
    add_test_questions()
    add_test_quiz()
    randomly_distribute_questions()
    show_tables()


if __name__ == "__main__":
    main()
