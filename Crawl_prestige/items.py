import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags
from .settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
import datetime

def remove_name(value):
    return value.replace("\n", "").replace("\t", "").replace("\xa0", ",")


def remove_time(value):
    return value.replace("min", "")


def prestige_image_url(value):
    return 'http://www.prestige-av.com'+value

def str_to_date(value):
    date = datetime.datetime.strptime(value.replace("/", "-"), SQL_DATE_FORMAT)
    return date


def prestige_remove_name(value):
    return value.replace("TKT", "").replace("GOOE", "")


class Prestige_itemloader(ItemLoader):
    default_output_processor = TakeFirst()

class Prestige_Item(scrapy.Item):
    video_number = scrapy.Field(
        input_processor=MapCompose(prestige_remove_name),
    )
    video_name = scrapy.Field(
        input_processor=MapCompose(remove_name),
    )
    actress = scrapy.Field(
        input_processor=MapCompose(remove_name),
    )
    video_lasts = scrapy.Field(
        input_processor=MapCompose(remove_time),
    )
    release_date = scrapy.Field(
        input_processor=MapCompose(str_to_date),
    )
    image_urls = scrapy.Field(
        output_processor=MapCompose(prestige_image_url),
    )
    image = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO prestige (video_number, video_name, actress, video_lasts, release_date) VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            self["video_number"], self["video_name"], self["actress"], self["video_lasts"], self["release_date"]
        )
        return insert_sql, params