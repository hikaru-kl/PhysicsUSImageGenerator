import logging
import PIL
import uuid
import random
import json
import math
import os
import zipfile
import PIL.Image

from urllib.request import urlretrieve
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT_DIR = os.path.abspath('.')

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def main(config: dict) -> None:
    tasks = data_loader(config)
    Y_MARGIN = config['y_margin_px']
    filename = f'variant_{str(uuid.uuid4())[:6]}.pdf'
    A4 = (1240, 1754)
    c = canvas.Canvas(filename, pagesize=A4)
    page_width, page_height = A4

    current_image_y = 0
    for i in range(1, len(tasks.keys())):

        # Scaling image
        image = PIL.Image.open(tasks[i])

        if image.width > page_width - 10:
            if config["debug"]:
                logger.info(
                    f'Image {tasks[i]} has been resized (image.width > page_width)')
            new_height = math.ceil(
                image.height * ((page_width - 10) / image.width))
            image = image.resize((page_width - 10, new_height))
        elif image.width < (page_width - 10) * 0.9:
            if config["debug"]:
                logger.info(
                    f'Image {tasks[i]} has been resized (image.width < page_width)')
            new_height = math.ceil(
                image.height * ((page_width - 10) / image.width))
            image = image.resize((page_width - 10, new_height))
        reportlab_pil_img = ImageReader(image)
        if i == 1:
            current_image_y = page_height - image.height - 10
        else:
            if current_image_y - image.height - Y_MARGIN >= Y_MARGIN:
                current_image_y -= image.height + Y_MARGIN
            else:
                c.showPage()
                current_image_y = page_height - image.height - Y_MARGIN
        c.drawImage(reportlab_pil_img, x=(
            page_width - reportlab_pil_img.getSize()[0]) / 2, y=current_image_y)
    c.save()
    logger.info(f'Вариант {filename} готов!')
    os.system('pause')


def data_loader(config: dict) -> dict:
    tasks = {}.fromkeys(range(1, config['tasks_amount'] + 1), [])
    for i in range(1, config['tasks_amount'] + 1):
        try:
            tasks[i] = os.path.abspath(
                ROOT_DIR + f'/data/{i}/{random.choice(os.listdir(path=ROOT_DIR + f"/data/{i}/"))}')
        except IndexError:
            logger.warning(f'Отсутствуют задания №{i}')
            del tasks[i]
            # time.sleep(0.1)
    return tasks


def initialization(config: dict):
    if config['debug']:
        logging.basicConfig(filename='app.log',
                            level=logging.DEBUG, encoding='utf-8', format='[%(asctime)s]%(levelname)s:%(message)s')
    else:
        logging.basicConfig(filename='app.log',
                            level=logging.INFO, encoding='utf-8', format='[%(asctime)s]%(levelname)s:%(message)s')
    if 'data' not in os.listdir(path=ROOT_DIR):
        try:
            urlretrieve(url=config['data_url'], filename='data.zip')
            with zipfile.ZipFile(ROOT_DIR + '/data.zip', 'r') as zip_ref:
                zip_ref.extractall(ROOT_DIR)
        except Exception as exp:
            if config['debug']:
                logger.error(f'Error while downloading data: {exp}')
            else:
                logger.info(
                    'Произошла ошибка при попытке скачать готовые задания.')
            os.mkdir(path=ROOT_DIR + '/data')
            for i in range(1, config['tasks_amount'] + 1):
                os.mkdir(path=ROOT_DIR + f'/data/{i}')
        else:
            try:
                os.remove(ROOT_DIR + '/data.zip')
            except:
                pass
            logger.info('Готовые задания успешно скачаны')
    logger.info('Данные успешно загружены')
    return main(config)


if __name__ == '__main__':
    default_config = {'tasks_amount': 26, 'debug': False,
                      'y_margin_px': 120, 'data_url': 'https://github.com/hikaru-kl/PhysicsUSImageGenerator/raw/main/data.zip'}
    if 'config.json' not in os.listdir(path=ROOT_DIR):
        json.dump(default_config, open('config.json', 'w'))
        config = default_config
    else:
        try:
            config: dict = json.load(open(ROOT_DIR + '/config.json', 'r'))
            if config.keys() != default_config.keys():
                raise
        except:
            config = default_config
            json.dump(default_config, open('config.json', 'w'))
    initialization(config)
