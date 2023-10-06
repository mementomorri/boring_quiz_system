from typing import NamedTuple

template = str


class Question(NamedTuple):
    id: int
    question: str
    answer: str
    wrong1: str
    wrong2: str
    wrong3: str


class Quiz(NamedTuple):
    id: int
    name: str


class QuizContent(NamedTuple):
    id: int
    quiz_id: int
    question_id: int
