from datetime import datetime
from datetime import timedelta
import requests
import os
from dotenv import load_dotenv
load_dotenv()
class BotSettings:
    sign_up_url = os.getenv('sign_up_url')
    meets_url = os.getenv('meets_url')
    jwt_token = None
    session = requests.Session()
    timings = {'refresh': int(os.getenv('refresh')), 'check_dates': int(os.getenv('check_dates'))}
    privous_check = privous_jwt = datetime.now()
class Bot(BotSettings):
    def __init__(self, token, chat_id,email,password):
        self.token = token
        self.chat_id = chat_id
        self.email = email
        self.password = password
    def update_jwt(self):
        headers = {"api_user":{"email":self.email,"password":self.password}}
        print(f"getting jwt: {datetime.now()}")

        try:
            response = self.session.post(url = self.sign_up_url,json = headers)
            self.jwt_token = response.json()['Authorization']
        except Exception as e:
            print(e)
    def check_dates(self):
        headers = {"Authorization":self.jwt_token}
        print(f"checking dates: {datetime.now()}")

        try:
            response = self.session.get(url = self.meets_url,headers =headers)
            return response.json()['meetings']
        except Exception as e:
            return {'error':e}
    def send_tg(self,date):
        id ,free,address,calendar_url = date['id'],date['capacity_free'],date['address'],date['calendar_url']
        message = f"link - {calendar_url}\nid - {id}\nсвободные места - {free}\nадресс - {address}\nhttps://applicant.21-school.ru/meet"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}"
        requests.get(url).json()
    def start_bot(self):
        if self.jwt_token is None:
            self.update_jwt()
        while True:
            time_now = datetime.now()
            if (time_now - self.privous_check) >= timedelta(seconds=self.timings['check_dates']):
                dates = self.check_dates()
                if 'error' in dates:
                    print(dates['error'])
                else:

                    for date in dates:
                        if date['capacity_free'] != 0:
                            self.send_tg(date)
                    self.privous_check = datetime.now()

            if (time_now - self.privous_jwt) >= timedelta(minutes=self.timings['refresh']):
                self.update_jwt()
                self.privous_jwt = datetime.now()
token = os.getenv('token')
id_channel = os.getenv('id_channel')
email = os.getenv('email')
password = os.getenv('password')
bot = Bot(token,id_channel,email,password)
bot.start_bot()

