class ConfigOnTest:
    SECRET_KEY = '88005553535лучшепозвонитьчемукоготозанимать'
    VK_ID = 8044414
    APP_URL = '127.0.0.1:5000'
    VK_SCOPE = 'friends'
    ADMIN_EMAIL = 'kolza2008@bk.ru'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PATH_TO_APP = "C:\projects\gamestore\\"
    NOTIFICATION_KEY = 'BCXEWPCfg8wIkw3DrXOyHNMWzzfEEFPAWnkBK95Hs9PNIOKDi2_I6IrCTtNbSu-Uxlx4dN2CGP0b9gJIuqD5gLQ'

class ConfigOnServer(ConfigOnTest):
    APP_URL = 'kolza2008.pythonanywhere.com'
    MAX_CONTENT_LENGHT = 100 * 1024 * 1024
    PATH_TO_APP = "/home/kolza2008/mysite/templates/"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://kolza2008:afganistan1457@kolza2008.mysql.pythonanywhere-services.com/kolza2008$main'
