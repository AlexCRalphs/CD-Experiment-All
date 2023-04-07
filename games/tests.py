from . import *
from otree.api import expect, Bot, Submission


class PlayerBot(Bot):

    def play_round(self):
        if self.round_number == 1:
            yield Submission(RandomiseGames, check_html=False, timeout_happened=True)
        yield Submission(GeneratePayoffs, check_html=False, timeout_happened=True)
        if (self.round_number % 2) == 0:
            yield DecisionPage, dict(choice='Top')
        else:
            yield DecisionPage, dict(choice='Bottom')
        if self.round_number == C.NUM_ROUNDS:
            yield Submission(ResultsCalculate, timeout_happened=True, check_html=False)
