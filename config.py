class ConfigOnTest:
    SECRET_KEY = '88005553535лучшепозвонитьчемукоготозанимать'
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PATH_TO_APP = "C:\projects\gamestore\\"

class ConfigOnServer:
    PATH_TO_APP = "/home/kolza2008/mysite/templates/"