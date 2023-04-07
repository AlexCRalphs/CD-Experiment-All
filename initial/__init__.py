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
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def make_field_2(label):
        return models.StringField(
            label=label,
            choices=["on"],
            blank=True,
        )

    participant_playing = models.BooleanField()
    player_id = models.IntegerField()
    force_start = models.BooleanField(blank=True, null=True)
    force_survey = models.BooleanField(blank=True, null=True)
    force_payoff = models.BooleanField(blank=True, null=True)
    force_finish = models.BooleanField(blank=True, null=True)

# FUNCTIONS


def set_player_ids(subsession: Subsession):
    import random
    secret_admin_participant_label = subsession.session.config['secret_admin_participant_label']
    subsession.session.vars['id_of_admin'] = float('inf')
    for p in subsession.get_players():
        if p.participant.label == secret_admin_participant_label:
            subsession.session.vars['id_of_admin'] = p.id_in_group
    if subsession.session.vars['id_of_admin'] != float('inf'):
        number_of_players = subsession.session.num_participants - 1
    else:
        number_of_players = subsession.session.num_participants
    player_ids = [*range(1, number_of_players + 1, 1)]
    random.shuffle(player_ids)
    print(player_ids)
    subsession.session.vars['player_ids'] = player_ids
    for p in subsession.get_players():
        set_player_id(p)


def set_player_id(player: Player):
    player_ids = player.session.vars['player_ids']
    id_in_group = player.id_in_group
    id_of_admin = player.session.vars['id_of_admin']
    if id_in_group < id_of_admin:
        player.participant.vars['player_id'] = player_ids[id_in_group-1]
        player.player_id = player_ids[id_in_group-1]
    elif id_in_group == id_of_admin:
        player.participant.vars['player_id'] = 0
        player.player_id = 0
    else:
        player.participant.vars['player_id'] = player_ids[id_in_group - 2]
        player.player_id = player_ids[id_in_group - 2]


# PAGES
class AdminPage(Page):
    form_model = 'player'
    form_fields = ['force_start',
                   'force_survey',
                   'force_payoff',
                   'force_finish']

    @staticmethod
    def vars_for_template(player):
        all_players = player.subsession.get_players()
        num_players_waiting_to_start = len ([ p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_to_start"] )
        num_waiting_for_survey = len([p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_for_survey"])
        num_waiting_for_payoff = len ([ p for p in all_players if 'status' in p.participant.vars and p.participant.status == "waiting_to_be_paid"] )
        num_players_in_session= len ([ p for p in all_players if 'status'in p.participant.vars and p.participant.status == "playing"])

        return{'num_players_waiting_to_start':num_players_waiting_to_start,
               'num_waiting_for_survey': num_waiting_for_survey,
               'num_waiting_for_payoff':num_waiting_for_payoff,
               'num_players_in_session':num_players_in_session}

    @staticmethod
    def is_displayed(player):
        # only appears if the participant_label is the secret_password
        return player.participant.label == player.session.config['secret_admin_participant_label']

    @staticmethod
    def error_message(player, values):
        if values['force_start']:
            player.session.start_all_together_admin = 1
        else:
            player.session.start_all_together_admin = 0

        if values['force_survey']:
            player.session.show_survey = 1
        else:
            player.session.show_survey = 0

        if values['force_payoff']:
            player.session.show_payoff = 1
        else:
            player.session.show_payoff = 0

        if values['force_finish']:
            player.session.finish_experiment = 1
        else:
            player.session.finish_experiment = 0

        return 'your action has been executed correctly: start set to ' + str(
            player.session.start_all_together_admin) + ' ' + str(
            player.session.show_survey) + ' ' + str(
            player.session.show_payoff) + ' ' + str(
            player.session.finish_experiment)


class Initiate_game(Page):
    timeout_seconds = 0

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['status'] = 'waiting_to_start'


class Before_experiment(Page):
    @staticmethod
    def get_timeout_seconds(player):
        if player.session.config['start_all_at_same_time'] == 1:
            return 0
        else:
            if 'start_all_together_admin' in player.session.vars and player.session.vars['start_all_together_admin'] == 1:
                return 0
            else:
                return int(60*player.session.config['time_to_complete'])

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['status'] = 'playing'
        player.participant_playing = True
        set_player_ids(player.subsession)


    @staticmethod
    def js_vars(player):
        if 'start_all_together_admin' in player.session.vars and player.session.start_all_together_admin:
            return dict(
                start=player.session.start_all_together_admin,
        )
        else:
            return dict(start=0)


page_sequence = [AdminPage, Initiate_game, Before_experiment]
