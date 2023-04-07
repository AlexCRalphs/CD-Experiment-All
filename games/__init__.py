from otree.api import *

author = "Alex Ralphs"

doc = """
The games in the experiments
"""


class C(BaseConstants):
    NAME_IN_URL = 'games'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 40
    INSTRUCTIONS_FILE = __name__ + '/Instructions.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    participant_code = models.StringField()
    participant_playing = models.BooleanField()
    player_id = models.IntegerField()
    AC_games = models.LongStringField()
    SH_games = models.LongStringField()
    choice = models.BooleanField(choices=[[True, 'Top'], [False, 'Bottom']])
    payoffs = models.LongStringField()
    paying_round = models.StringField()
    choices = models.StringField()
    opponent_choices = models.StringField()
    opponent_payment_choices = models.StringField()
    payment_payoffs = models.LongStringField()
    finished_late = models.IntegerField(initial=0)


# FUNCTIONS
def creating_session(subsession: Subsession):
    # create all of the payoffs for the games
    import random  # create 2 lists of games (AC and SH), and randomise them
    # import csv
    import pandas as pd
    number_of_games = subsession.session.config['number_of_games']
    for p in subsession.get_players():
        dict_ac = {}
        dict_sh = {}
        filename_ac = "Game_Payoffs_AC.csv"
        filename_sh = "Game_Payoffs_SH.csv"
        payoff_index = ["name", "T", "R", "S", "P"]
        ac_games = pd.read_csv(filename_ac, usecols=payoff_index)
        sh_games = pd.read_csv(filename_sh, usecols=payoff_index)
        ac = []
        sh = []
        for i in range(30):
            ac.append(dict(x1=int(ac_games.loc[i, 'R']), x2=int(ac_games.loc[i, 'S']), x3=int(ac_games.loc[i, 'T']),
                           x4=int(ac_games.loc[i, 'P'])))
            dict_ac[ac_games.loc[i, 'name']] = ac[i]
        for i in range(10):
            sh.append(dict(x1=int(sh_games.loc[i, 'R']), x2=int(sh_games.loc[i, 'S']), x3=int(sh_games.loc[i, 'T']),
                           x4=int(sh_games.loc[i, 'P'])))
            dict_sh[sh_games.loc[i, 'name']] = sh[i]
        p.participant.vars['AC_payoffs'] = dict_ac
        p.participant.vars['SH_payoffs'] = dict_sh


        # with open(filename_ac, 'r') as data:
        #    reader = csv.DictReader(data, dialect='excel')
        #    keys = []
        #    ac = []
        #    for row in reader:
        #        line = dict(row)
        #        keys.append(line['name'])
        #        ac.append(dict(x1=int(line['R']), x2=int(line['S']), x3=int(line['T']), x4=int(line['P'])))
        #    for i in range(len(keys)):
        #        dict_ac[keys[i]] = ac[i]
        #    p.participant.vars['AC_payoffs'] = dict_ac
        # with open(filename_sh, 'r') as data:
        #    reader = csv.DictReader(data, dialect='excel')
        #    keys = []
        #    sh = []
        #    for row in reader:
        #        line = dict(row)
        #        keys.append(line['name'])
        #        sh.append(dict(x1=int(line['R']), x2=int(line['S']), x3=int(line['T']), x4=int(line['P'])))
        #    for i in range(len(keys)):
        #        dict_sh[keys[i]] = sh[i]
        #    p.participant.vars['SH_payoffs'] = dict_sh

        if subsession.round_number == 1:
            paying_round = random.sample(range(1, number_of_games + 1), k=1)
            p.participant.vars['paying_round'] = paying_round


def set_payoffs(subsession: Subsession):
    secret_admin_participant_label = subsession.session.config['secret_admin_participant_label']
    for player in subsession.get_players():
        if player.participant.label != secret_admin_participant_label:
            set_payoff(player)


def randomise_games(player: Player):
    import random
    ac_game_payoffs = player.participant.vars['AC_payoffs']
    sh_game_payoffs = player.participant.vars['SH_payoffs']
    num_ac_games = int(len(ac_game_payoffs))
    num_sh_games = int(len(sh_game_payoffs))
    gap = player.session.config['gap_between_alternative_games']
    freq_sh = gap + 1
    ac = []
    sh = []
    for i in range(num_ac_games):
        x = i + 1
        ac.append(x)
    for i in range(num_sh_games):
        x = i + 1
        sh.append(x)
    random.shuffle(ac)
    random.shuffle(sh)
    ac_games = dict()
    sh_games = dict()
    game_ids = dict()
    for i in range(num_ac_games):
        index_ac = 'AC' + str(ac[i])
        index = str(i + 1)
        ac_games[index] = (ac_game_payoffs[index_ac])
    for i in range(num_sh_games):
        index_sh = "SH" + str(sh[i])
        index = str(i + 1)
        sh_games[index] = (sh_game_payoffs[index_sh])
    for i in range(C.NUM_ROUNDS):
        game_index = str(i + 1)
        if (i % freq_sh) == gap:
            sh_index = (i - gap) // freq_sh
            index = "SH" + str(sh[sh_index])
        else:
            q, r = divmod(i, freq_sh)
            ac_index = i - q
            index = 'AC' + str(ac[ac_index])
        game_ids[game_index] = index

    player.AC_games = str(ac_games)
    player.SH_games = str(sh_games)
    player.participant.vars['ac_games'] = ac_games
    player.participant.vars['sh_games'] = sh_games
    player.participant.vars['game_ids'] = game_ids
    player.participant_code = player.participant.code
    player.participant_playing = True
    player.player_id = player.participant.vars['player_id']


def generate_payoffs(player: Player):
    ac_game_payoffs = player.participant.vars['AC_payoffs']
    sh_game_payoffs = player.participant.vars['SH_payoffs']
    num_ac_games = int(len(ac_game_payoffs))
    num_sh_games = int(len(sh_game_payoffs))
    num_games = num_sh_games + num_ac_games
    payoffs = []
    ac_games = player.participant.vars['ac_games']
    sh_games = player.participant.vars['sh_games']
    round_number = player.round_number
    gap = player.session.config['gap_between_alternative_games']
    freq_sh = gap + 1
    if (round_number % freq_sh) == 0:
        index_game = int(round_number / freq_sh)
        for i in range(1, 5):
            index_payoff = 'x' + str(i)
            payoffs.append(sh_games[str(index_game)][index_payoff])
    else:
        q, r = divmod(round_number, freq_sh)
        index_game = int(round_number - q)
        for i in range(1, 5):
            index_payoff = 'x' + str(i)
            payoffs.append(ac_games[str(index_game)][index_payoff])
    player.payoffs = " ".join(str(e) for e in payoffs)


def set_payoff(player: Player):
    choice = []
    opponent_choices = []
    opponent_payment_choices = []
    paying_round = player.participant.vars['paying_round']
    player.paying_round = str(paying_round)
    payment_payoffs = []
    results_payments = []
    player_id = player.participant.vars['player_id']
    others = player.get_others_in_group()
    if (player_id % 2) == 0:
        for o in others:
            opponent_id = o.participant.vars['player_id']
            if opponent_id == player_id - 1:
                opponent = o
    else:
        if player_id == player.session.num_participants:
            opponent = player.group.get_player_by_id(1)
        else:
            for o in others:
                opponent_id = o.participant.vars['player_id']
                if opponent_id == player_id + 1:
                    opponent = o
    opponent_game_id = opponent.participant.vars['game_ids']
    opponent_games = []
    player_game_id = player.participant.vars['game_ids']
    player_games = []
    for i in range(C.NUM_ROUNDS):
        opponent_choices.append(int(opponent.in_round(i + 1).choice))
        opponent_games.append(opponent_game_id[str(i + 1)])
        player_games.append(player_game_id[str(i + 1)])

    choice.append(int(player.in_round(paying_round[0]).choice))
    results_payoffs = player.in_round(paying_round[0]).payoffs.split()
    payment_payoffs.append(' '.join(results_payoffs))
    for j in range(C.NUM_ROUNDS):
        if opponent_games[j] == player_games[paying_round[0] - 1]:
            opponent_payment_choices.append(opponent_choices[j])
    if opponent_payment_choices[0] == 1:
        if choice[0]:
            results_payments.append(int(results_payoffs[0]))
        else:
            results_payments.append(int(results_payoffs[2]))
    else:
        if choice[0]:
            results_payments.append(int(results_payoffs[1]))
        else:
            results_payments.append(int(results_payoffs[3]))
    player.choices = "".join(str(e) for e in choice)
    player.opponent_choices = "".join(str(e) for e in opponent_choices)
    player.opponent_payment_choices = "".join(str(e) for e in opponent_payment_choices)
    player.payment_payoffs = " ".join(str(e) for e in payment_payoffs)

    player.participant.payoff = sum(results_payments)

    player.participant.payment_payoffs = player.payment_payoffs
    player.participant.choices = player.choices
    player.participant.opponent_payment_choices = player.opponent_payment_choices


# PAGES
class RandomiseGames(Page):
    timeout_seconds = 0

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player = player
        timeout_happened = timeout_happened
        if timeout_happened:
            randomise_games(player)


class GeneratePayoffs(Page):
    timeout_seconds = 0

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player = player
        timeout_happened = timeout_happened
        if timeout_happened:
            generate_payoffs(player)


class DecisionPage(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player):
        return dict(payoffs=player.payoffs.split(),
                    number_of_games=player.session.config['number_of_games'],
                    time=player.session.config['decision_page_time'])

    @staticmethod
    def js_vars(player):
        return dict(time=player.session.config['decision_page_time'])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            player.participant.status = "waiting_for_survey"


class ResultsCalculate(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS and player.finished_late == 0

    @staticmethod
    def get_timeout_seconds(player):
        if 'show_survey' in player.session.vars and player.session.vars['show_survey'] == 1:
            return 0
        else:
            return int(60 * 1000)

    @staticmethod
    def js_vars(player):
        if 'show_payoff' in player.session.vars and player.session.vars['show_survey']:
            return dict(showsurvey=player.session.vars['show_survey'])
        else:
            return dict(showsurvey=0)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoffs(player.subsession)


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(number_of_games=player.session.config['number_of_games'])


page_sequence = [RandomiseGames, GeneratePayoffs, DecisionPage, ResultsCalculate]
