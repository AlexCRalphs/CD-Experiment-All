from . import *
from otree.api import expect, Bot, Submission


class PlayerBot(Bot):

    def play_round(self):
        if self.player.participant.label == self.session.config['secret_admin_participant_label']:
            yield AdminPage, dict(force_start=0, force_payoff=0, force_finish=0)
        else:
            yield Submission(Initiate_game, check_html=False)
            yield Before_experiment
