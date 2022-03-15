class ConfigOnTest:
    SECRET_KEY = '88005553535лучшепозвонитьчемукоготозанимать'
    VK_ID = 8044414
    APP_URL = '127.0.0.1:5000'
    VK_SCOPE = 'friends'
    ADMIN_EMAIL = 'kolza2008@bk.ru'
    MAIL_PASSWORD = 'Da_i_Gen1y'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'imperativgames@gmail.com'
    MAIL_DEFAULT_SENDER = 'imperativgames@gmail.com'  
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PATH_TO_APP = "C:\\Users\\kolza2008\\projects\\gamestory\\"
    NOTIFICATION_KEY = 'BCXEWPCfg8wIkw3DrXOyHNMWzzfEEFPAWnkBK95Hs9PNIOKDi2_I6IrCTtNbSu-Uxlx4dN2CGP0b9gJIuqD5gLQ'

class ConfigOnServer(ConfigOnTest):
    APP_URL = 'kolza2008.pythonanywhere.com'
    MAX_CONTENT_LENGHT = 108 * 1024 * 1024
    PATH_TO_APP = "/home/kolza2008/mysite/"
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://kolza2008:afganistan1457@kolza2008.mysql.pythonanywhere-services.com/kolza2008$main5'
