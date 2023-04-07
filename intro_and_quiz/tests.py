from . import *
from otree.api import expect, Bot, Submission


class PlayerBot(Bot):

    def play_round(self):
        yield Intro
        yield Submission(Instructions1, timeout_happened=True)
        yield Submission(Instructions2, timeout_happened=True, check_html=False)
        yield Submission(Quiz, dict(quiz_q1=1, quiz_q2=1, quiz_q3=4, quiz_q4=1), check_html=False)
        yield PostQuiz
