"""
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы

результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.

пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import time
import json
from pathlib import Path
import requests

class Parse5ka:

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0"}

    def __init__(self, categories_url: str,start_url: str, save_path: Path):
        self.start_url = start_url
        self.categories_url = categories_url
        self.save_path = save_path

    def _get_response(self, url: str, params: dict):
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for category in self._parse_cat(self.categories_url):
            category_path = self.save_path.joinpath(f"{category['parent_group_code']}.json")
            category_data=[]
            for product in self._parse(self.start_url,{'categories':category['parent_group_code']}):
                category_data.append(product)
            category_data={'name':category['parent_group_name'],
                           'code':category['parent_group_code'],
                           'products': category_data}
            self._save(category_data, category_path)

    def _parse(self, url: str, params: dict = {}):
        while url:
            response = self._get_response(url,params)
            data: dict = response.json()
            url = data['next']
            for product in data["results"]:
                yield product

    def _parse_cat(self, url: str, params: dict = {}):
            response = self._get_response(url,params)
            data: dict = response.json()
            for category in data:
                yield category

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False),encoding='utf8')


if __name__ == '__main__':
    cat_url = 'https://5ka.ru/api/v2/categories/'
    url = 'https://5ka.ru/api/v2/special_offers/'
    save_path = Path(__file__).parent.joinpath('products')
    if not save_path.exists():
        save_path.mkdir()

    parser = Parse5ka(cat_url, url, save_path)
    parser.run()

