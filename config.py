import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '<replace with a secret key>')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '<replace with a secret key>')

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGO_DB', 'mongodb://localhost:27017/blog_dev')
    }
    PROFILER_DIR = None  # Directory where profiler data files are saved.
    PROFILER_NUM_FUNCTION_RESTRICTIONS = 25  # Number of functions to include in the profiler report.

    @classmethod
    def init_app(cls, app):
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[cls.PROFILER_NUM_FUNCTION_RESTRICTIONS],
                                          profile_dir=cls.PROFILER_DIR)


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGO_DB', 'mongodb://localhost:27017/blog_dev')
    }
    LOGGING_FILENAME = 'log/prod.log'

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(cls.LOGGING_FILENAME, maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGO_DB', 'mongodb://localhost:27017/api_blog_test')
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}