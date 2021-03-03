import re

import scrapy
from ..loaders import AutoyoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    _xpath_selectors = {
        "brands": "//div[@data-target='transport-main-filters']/"
        "div[contains(@class, 'TransportMainFilters_brandsList')]//"
        "a[@data-target='brand']/@href",
        "pagination": "//div[contains(@class, 'Paginator_block')]//"
                  "a[@data-target='button_link']/@href",
        "car": "//div[contains(@class, 'SerpSnippet_titleWrapper')]//"
                      "a[@data-target='serp-snippet-title']/@href"
    }
    _car_xpaths = {
        "title": "//div[@data-target='advert-title']/text()",
        "photos": "//figure/picture/img/@src",
        "characteristics": "//h3[contains(text(), 'Характеристики')]/..//"
        "div[contains(@class, 'AdvertSpecs_row')]",
        "descriptions": "//div[@data-target='advert-info-descriptionFull']/text()",
        "price": "//div[@data-target='advert-price']/text()"
    }

    @staticmethod
    def get_author_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return resp.urljoin(f"/user/{result[0]}") if result else None
            except TypeError:
                pass

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get("href")
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def _get_follow_xpath(self, response, select_str, callback, **kwargs):
        for link in response.xpath(select_str):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["brands"], self.brand_parse
        )

    def brand_parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["pagination"], self.brand_parse
        )
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["car"], self.car_parse
        )

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        loader.add_value("author", AutoyoulaSpider.get_author_id(response))
        for key, xpath in self._car_xpaths.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
