from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose
from .items import GbAutoYoulaItem


def get_characteristics(item):
    selector = Selector(text=item)
    data = {
        "name": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_label')]/text()"
        ).extract_first(),
        "value": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_data')]//text()"
        ).extract_first(),
    }
    return data


class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    descriptions_out = TakeFirst()
    price_out = TakeFirst()
    author_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
