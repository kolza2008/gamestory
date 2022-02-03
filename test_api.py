import requests

SERVER_URL = "http://127.0.0.1:5000" #"https://kolza2008.pythonanywhere.com" #
CODE_UNDER = 795450
CODE_TOP = 960335

token_rq = requests.get(f'{SERVER_URL}/api/login/token/{CODE_UNDER*CODE_TOP}')
token = token_rq.text.split('\n')
SECRET_KEY = (int(token[0]) - CODE_TOP) // CODE_UNDER

print(f'{SERVER_URL}/api/login?token={":".join(token)}')
while True:
    valid = requests.get(f'{SERVER_URL}/api/check_valid/{token[1]}')
    if valid.text == '1':
        break
print('You is authentificated')

while True:
    method = input('Method: ')
    if method == 'esc': break
    args = input('Arguments(splitter is ,): ').split(',')
    if args != ['']:
        request = requests.get(f'{SERVER_URL}/api/{method}/{"/".join(args)}?token={":".join(token)}')
    else:
        request = requests.get(f'{SERVER_URL}/api/{method}?token={":".join(token)}')
    if request.status_code == 200:
        print('Server answer: ', request.text)
        token[0] = str(int(token[0]) * CODE_UNDER // CODE_TOP - SECRET_KEY)
    else:
        print(f'Server status is bad.It is {request.status_code}')