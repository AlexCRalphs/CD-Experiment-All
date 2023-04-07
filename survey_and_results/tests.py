from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Survey, dict(gender="Male", age=28, nationality="UK", student="Graduate", area="Economics",
                                      decision_description="Bots Bots Bots"), check_html=False)
        yield Submission(PaymentInfo, dict(email="alexanderralphs@gmail.com", country="UK"), check_html=False)
        yield Submission(ResultsWaitPage, timeout_happened=True, check_html=False)
        yield Results
