from celery import Celery
from config.config import ConfigResult

config: ConfigResult = ConfigResult('.env')

app = Celery(main = config.celery.imports[0], broker=config.celery.broker_url)
app.autodiscover_tasks()
app.conf.update(timezone='Europe/Moscow')