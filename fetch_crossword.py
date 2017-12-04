import requests
from bs4 import BeautifulSoup
from time import time 
from datetime import datetime

def _login_to_nyt(session, username, password):
    """Login to NYT account.

    Args:
        session (requests.Session): session object
        username (str): username associated with account
        password (str): password for account
    """
    print 'Logging in to NYT...'
    login_url = 'https://myaccount.nytimes.com/auth/login'
    login_page = session.get(login_url)
    loginSoup = BeautifulSoup(login_page.text, 'html.parser')

    token = loginSoup.find('input', {'name': 'token'})['value']
    expires = int(round(time() * 1000)) + 60000
    data = {'userid': username, 'password': password, 'token': token,
            'remember': True, 'is_continue': False, 'expires': expires} 
    login = session.post(login_url, data=data)

def _get_crossword_data(session):
    """Fetch crossword data using the currently logged in session.

    Args:
        session (requests.Session): session object
    """
    today = datetime.today()
    month = today.month
    day = today.day
    if today.month < 10:
        month = '0{}'.format(today.month) 
    if today.day < 10:
        day = '0{}'.format(today.day) 
    crossword_url = 'http://www.nytimes.com/svc/crosswords/v2/puzzle/daily-{}-'\
                    '{}-{}.json'.format(today.year, month, day) 
    
    print crossword_url
    crossword_data = session.get(crossword_url)
    return crossword_data.json()['results'][0]['puzzle_data']

def get_crossword(email, password):
    session = requests.session()
    _login_to_nyt(session, email, password)
    return _get_crossword_data(session)
