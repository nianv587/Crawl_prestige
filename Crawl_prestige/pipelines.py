import copy
import scrapy
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        #不同于直接创建数据库连接, 使用adbapi.ConnectionPool类来管理连接.可以让adbapi来使用多个连接, 比如每个线程一个连接
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, copy.deepcopy(item))
        query.addErrback(self.handle_error)


    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class PrestigePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url, meta={'item': item, 'name': item['video_number'], 'index': item['image_urls'].index(image_url)})

    def file_path(self, request, response=None, info=None):
        name = request.meta['name']
        index = request.meta['index']  # 通过上面的index传递过来列表中当前下载图片的下标
        try:
            image_guid = name + '_' + str(index) + '.' + request.url.split('/')[-1].split('.')[-1]
            filename = u'/{0}/{1}'.format(name, image_guid)
        except Exception as e:
            print(e)
        return filename

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item