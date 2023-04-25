from os import environ

SESSION_CONFIGS = [
    dict(
        name='anti_co_ordination_game',
        participation_fee=10,
        num_demo_participants=10,
        app_sequence=['initial', 'intro_and_quiz', 'games', 'survey_and_results'],
        number_of_games=40,
        gap_between_alternative_games=3,
        instructions_time_sec_1=60,
        instructions_time_sec_2=60,
        decision_page_time=20,
        secret_admin_participant_label="justadmin877012",
        start_all_at_same_time=0,
        show_payoff_right_away=0,
        show_payoff_when_all_done=0,
        time_to_complete=90,
        use_browser_bots=False,
    ),
]

# http://localhost:8000/room/alex_test/?participant_label=justadmin877012

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['expiry', 'status', 'quiz_number_correct', 'quiz_incorrect_count', 'quiz_finished',
                      'paying_round', 'player_id', 'game_payoff', 'payment_payoffs', 'choices', 'AC_payoffs',
                      'SH_payoffs', 'ac_games', 'sh_games', 'games_finished', 'game_ids', 'opponent_payment_choices']
SESSION_FIELDS = ['start_all_together_admin', 'show_payoff', 'show_survey', 'finish_experiment', 'player_ids',
                  'ids_excluded', 'ids_not_excluded', 'id_of_admin']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

ROOMS = [
    dict(
        name='alex_test',
        display_name='Anti-coordination Game - Alex Test',
        # participant_label_file='_rooms/ELFE.txt',
    ),
    dict(
        name='Live',
        display_name='Anti-coordination Game - Live',
        # participant_label_file='_rooms/ELFE.txt',
    ),
]

SECRET_KEY = '1827262100741'

INSTALLED_APPS = ['otree']
