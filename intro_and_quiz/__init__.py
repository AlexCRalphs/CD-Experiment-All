from otree.api import *

author = "Alex Ralphs"

doc = """
Intro and Quiz
"""


class C(BaseConstants):
    NAME_IN_URL = 'intro_and_quiz'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INSTRUCTIONS_FILE = __name__ + '/Instructions.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    participant_code = models.StringField()
    participant_playing = models.BooleanField()
    player_id = models.IntegerField()
    quiz_finished = models.BooleanField()
    quiz_incorrect_count = models.IntegerField(initial=0, max=8)
    quiz_number_correct = models.IntegerField()

    quiz_q1 = models.IntegerField(choices=[[1, '1'], [2, '2']], widget=widgets.RadioSelect,
                                  blank=True)  # True False question
    quiz_q2 = models.IntegerField(choices=[[1, '1'], [2, '2']], widget=widgets.RadioSelect,
                                  blank=True)  # True of False
    quiz_q3 = models.IntegerField(choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4']], widget=widgets.RadioSelect,
                                  blank=True)  # 4 option question
    quiz_q4 = models.IntegerField(choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4']], widget=widgets.RadioSelect,
                                  blank=True)  # 4 option question


# FUNCTIONS

def set_player_id(player: Player):
    player.participant_playing = True
    player.player_id = player.participant.vars['player_id']


# PAGES
class Intro(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(participation_fee=player.session.config['participation_fee'],
                    max_payment=cu(34) + player.session.config['quiz_payment'],
                    min_payment=cu(5))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_player_id(player)


class Instructions1(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(participation_fee=player.session.config['participation_fee'],
                    instruction_time=player.session.config['instructions_time_sec_2'])

    @staticmethod
    def js_vars(player):
        return dict(instruction_time=player.session.config['instructions_time_sec_1'])


class Instructions2(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(number_of_games=player.session.config['number_of_games'],
                    instruction_time=player.session.config['instructions_time_sec_2'],
                    time=player.session.config['decision_page_time'])

    @staticmethod
    def js_vars(player):
        return dict(instruction_time=player.session.config['instructions_time_sec_2'])


class Quiz(Page):
    form_model = 'player'
    form_fields = ['quiz_q1', 'quiz_q2', 'quiz_q3', 'quiz_q4']

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        my_id = player.id_in_group
        if 0 not in data[0:3]:
            group.get_player_by_id(my_id).quiz_incorrect_count += 1
        if group.get_player_by_id(my_id).quiz_incorrect_count <= 1:
            group.get_player_by_id(my_id).quiz_number_correct = data[4]
        if data[0] == 1 and data[1] == 1 and data[2] == 4 and data[3] == 1:
            group.get_player_by_id(my_id).quiz_finished = True
            response = dict(type='quiz_finished')
            group.get_player_by_id(my_id).quiz_incorrect_count -= 1
            return {my_id: response}
        elif group.get_player_by_id(my_id).quiz_incorrect_count == 10:
            response = dict(type='max_incorrect_count')
            return {my_id: response}

    @staticmethod
    def vars_for_template(player):
        return dict(number_of_games=player.session.config['number_of_games'],
                    instruction_time=player.session.config['instructions_time_sec_2'],
                    time=player.session.config['decision_page_time'])

    # @staticmethod
    # def error_message(player, values):
        # if not player.quiz_finished:
            # return 'At least one of your answers is wrong.'


class PostQuiz(Page):
    pass


class Instructions(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(number_of_games=player.session.config['number_of_games'])


page_sequence = [Intro, Instructions1, Instructions2, Quiz, PostQuiz]
