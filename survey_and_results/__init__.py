from otree.api import *

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import urllib

author = 'Alex Ralphs'

doc = """
Survey and Results pages
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey_and_results'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INSTRUCTIONS_FILE = __name__ + '/Instructions.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField(choices=['Male', 'Female', 'Non-binary', 'Prefer no to say'],
                                widget=widgets.RadioSelect)
    age = models.StringField(blank=True)
    nationality = models.StringField(blank=True)
    student = models.StringField(choices=['Undergraduate', 'Graduate'], widget=widgets.RadioSelect, blank=True)
    area = models.StringField(choices=['Biology', 'Business', 'ComSci', 'Economics', 'Engineering', 'History', 'Maths',
                                       'Physics', 'PolSci', 'Psych', 'Other'], widget=widgets.RadioSelect, blank=True)
    decision_description = models.LongStringField(blank=True)
    email = models.StringField(blank=True)
    participant_name = models.StringField(blank=True)
    country = models.StringField(blank=True)

    finished_late = models.IntegerField(initial=0)

    def validateEmail(player, email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def email_address_error_message(player, value):
        if value:
            if not player.validateEmail(value):
                return "Email address format is not valid"


# PAGES
class Survey(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'nationality', 'student', 'area', 'decision_description']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if 'finish_experiment' in player.session.vars and player.session.vars['finish_experiment'] == 1:
            player.finished_late = 1
        else:
            player.finished_late = 0


class PaymentInfo(Page):
    form_model = 'player'
    form_fields = ['email', 'participant_name', 'country']

    @staticmethod
    def is_displayed(player: Player):
        return player.finished_late == 0

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.status = "waiting_to_be_paid"


class ResultsWaitPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.finished_late == 0

    @staticmethod
    def get_timeout_seconds(player):
        if player.session.config['show_payoff_right_away'] == 1:
            return 0
        elif player.session.config['show_payoff_when_all_done'] == 1:
            return 0
        else:
            if 'show_payoff' in player.session.vars and player.session.vars['show_payoff'] == 1:
                return 0
            else:
                return int(60*1000)

    @staticmethod
    def js_vars(player):
        if 'show_payoff' in player.session.vars and player.session.vars['show_payoff']:
            return dict(showpayoff=player.session.vars['show_payoff'])
        else:
            return dict(showpayoff=0)


class Results(Page):
    form_model = 'player'

    @staticmethod
    def live_method(player, data):
        import pandas as pd
        if data['send_email'] == 1:
            attachment_name = "payment_info.png"
            send_to_email = "{}".format(data["email_address"])
            data = data["attachment"]
            response = urllib.request.urlopen(data)
            with open(attachment_name, 'wb') as f:
                f.write(response.file.read())

            def send_mail(send_from, send_to, subject, message, files=[],
                          server="smtp.gmail.com", port=587, username='', password='',
                          use_tls=True):
                """Compose and send email with provided info and attachments.

                Args:
                    send_from (str): from name
                    send_to (list[str]): to name(s)
                    subject (str): message title
                    message (str): message body
                    files (list[str]): list of file paths to be attached to email
                    server (str): mail server host name
                    port (int): port number
                    username (str): server auth username
                    password (str): server auth password
                    use_tls (bool): use TLS mode
                """
                msg = MIMEMultipart()
                msg['From'] = send_from
                msg['To'] = ', '.join(send_to)
                msg['Date'] = formatdate(localtime=True)
                msg['Subject'] = subject

                msg.attach(MIMEText(message, "html"))

                for path in files:
                    part = MIMEBase('application', "octet-stream")
                    with open(path, 'rb') as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    'attachment; filename={}'.format(Path(path).name))
                    msg.attach(part)

                smtp = smtplib.SMTP(server, port)
                if use_tls:
                    smtp.starttls()
                smtp.login(username, password)
                smtp.sendmail(send_from, send_to, msg.as_string())
                smtp.quit()

            html = """\
            <html>
              <body>
                <p>Please find attached your payment details for today's experiment. <br> <br> The ELFE team
                </p>
              </body>
            </html>
            """
            email_details = pd.read_csv('email_details.csv', usecols=['Host_email', 'username', 'password'])
            host_email = email_details.loc[0, 'Host_email']
            username = email_details.loc[0, 'username']
            password = email_details.loc[0, 'password']
            send_mail(host_email, [send_to_email],
                      "Your payment details - ELFE experiment", html,
                      files=[attachment_name], server="smtp.gmail.com",
                      port=587,
                      username=username,
                      password=password,
                      use_tls=True)
            return {player.id_in_group: "Email successfully sent"}

    @staticmethod
    def is_displayed(player: Player):
        return player.finished_late == 0

    @staticmethod
    def vars_for_template(player: Player):
        payoff_total = player.participant.payoff_plus_participation_fee()
        return dict(participation_fee=int(player.session.config['participation_fee']),
                    payoff_total=int(payoff_total),
                    payoff=player.participant.payoff,
                    paying_round=player.participant.vars['paying_round'],
                    payoffs_1=player.participant.payment_payoffs.split(),
                    choices=player.participant.choices,
                    opponent_choices=player.participant.opponent_payment_choices)

    @staticmethod
    def js_vars(player: Player):
        return dict(choices=player.participant.choices,
                    opponent_choices=player.participant.opponent_payment_choices,
                    email_address=player.email)


page_sequence = [Survey, PaymentInfo, ResultsWaitPage, Results]
