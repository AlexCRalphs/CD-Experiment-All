from otree.api import *

import time

author = 'Alex Ralphs'

doc = """
Application to manually select when experiments start.
"""


class C(BaseConstants):
    NAME_IN_URL = 'initial'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    time_webpage = 0


class Subsession(BaseSubsession):
    def creating_session(subsession):
        for p in subsession.get_players():
            p.participant.expiry = (time.time() + subsession.session.config['time_to_complete'] * 60)
            p.participant.status = "waiting_to_start"


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.IntegerField()

    def make_field_2(label):
        return models.StringField(
            label=label,
            choices=["on"],
            blank=True,
        )

    force_start = models.BooleanField(blank=True, null=True)
    force_survey = models.BooleanField(blank=True, null=True)
    force_payoff = models.BooleanField(blank=True, null=True)
    force_finish = models.BooleanField(blank=True, null=True)


# PAGES
class AdminPage(Page):
    form_model = 'player'
    form_fields = ['force_start',
                   'force_survey',
                   'force_payoff',
                   'force_finish']

    @staticmethod
    def vars_for_template(subsession):
        all_players = subsession.get_players()
        num_players_waiting_to_start = len ([ p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_to_start"] )
        num_waiting_for_survey = len([ p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_for_survey"])
        num_waiting_for_payoff = len ([ p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_to_be_paid"] )
        num_players_in_session= len ([ p for p in all_players if 'status'in p.participant.vars and p.participant.status == "playing"])

        return{'num_players_waiting_to_start':num_players_waiting_to_start,
               'num_waiting_for_survey':num_waiting_for_survey,
               'num_waiting_for_payoff':num_waiting_for_payoff,
               'num_players_in_session':num_players_in_session}

    @staticmethod
    def is_displayed(player, participant, session):
        # only appears if the participant_label is the secret_password
        return player.participant.label == session.config['secret_admin_participant_label']

    @staticmethod
    def error_message(session, values):
        if values['force_start']:
            session.start_all_together_admin = 1
        else:
            session.start_all_together_admin = 0

        if values['force_survey']:
            session.show_survey = 1
        else:
            session.show_survey = 0

        if values['force_payoff']:
            session.show_payoff = 1
        else:
            session.show_payoff = 0

        if values['force_finish']:
            session.finish_experiment = 1
        else:
            session.finish_experiment = 0

        return 'your action has been executed correctly: start set to ' + str(
            session.start_all_together_admin) + ' ' + str(
            session.show_survey) + ' ' + str(
            session.show_payoff) + ' ' + str(
            session.finish_experiment)


class Initiate_game(Page):
    pass


class Before_experiment(Page):
    @staticmethod
    def get_timeout_seconds(session):
        if session.config['start_all_at_same_time'] == 1:
            return 0
        else:
            if 'start_all_together_admin' in session.vars and session.vars['start_all_together_admin'] == 1:
                return 0
            else:
                return int(60*session.config['time_to_complete'])

    @staticmethod
    def before_next_page(player, participant):
        player.participant.vars['status'] = 'playing'

    @staticmethod
    def js_vars(session):
        if 'start_all_together_admin' in session and session.start_all_together_admin:
            return dict(
                start=session.start_all_together_admin,
        )
        else:
            return dict(start=0)


page_sequence = [AdminPage, Initiate_game, Before_experiment]
