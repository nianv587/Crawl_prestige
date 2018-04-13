import scrapy
from scrapy.http import Request
from Crawl_prestige.items import Prestige_Item,Prestige_itemloader
from urllib import parse
class PrestigeSpider(scrapy.Spider):
    name = 'prestige'
    cookies = [
        {'httpOnly': False, 'secure': False, 'name': 'coc', 'domain': 'www.prestige-av.com', 'path': '/', 'value': '1'},
        {'httpOnly': False, 'secure': False, 'expiry': 1504847378, 'name': 'age_auth', 'domain': '.prestige-av.com', 'path': '/', 'value': '1'},
        {'httpOnly': False, 'secure': False, 'name': 'PSID', 'domain': '.prestige-av.com', 'path': '/', 'value': '546d7d8jfllge7ufjm142lst01'},
        {'httpOnly': False, 'secure': False, 'expiry': 1504242646, 'name': '_gat', 'domain': '.prestige-av.com', 'path': '/', 'value': '1'},
        {'httpOnly': False, 'secure': False, 'expiry': 1504328986, 'name': '_gid', 'domain': '.prestige-av.com', 'path': '/', 'value': 'GA1.2.291182835.1504242586'},
        {'httpOnly': False, 'secure': False, 'expiry': 1567314586, 'name': '_ga', 'domain': '.prestige-av.com', 'path': '/', 'value': 'GA1.2.1415600803.1504242586'}
    ]


    def start_requests(self):
        yield scrapy.Request('http://www.prestige-av.com/release/release_list.php', cookies=self.cookies, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response):
        list_nodes = response.xpath('//div[@class="box_705"]//p[@class="align_right"]/a')
        for list_node in list_nodes:
            list_url = list_node.xpath("@href").extract_first()
            yield Request(url=parse.urljoin(response.url, list_url), callback=self.parse)

    def parse(self, response):
        video_nodes = response.xpath('//ul[@class="list_layout_01"]/li/a')
        for video_node in video_nodes:
            video_url = video_node.xpath("@href").extract_first()
            yield Request(url=parse.urljoin(response.url, video_url), callback=self.parse_detail)
        # 通过xpath获取一页的地址后再获取下一页的地址
        urls = response.xpath('//div[@class="box_705"]/div[@class="search_pager_layout_01"]//ul[@class="pager_layout_01"]/li/a/@href').extract()
        next_index = response.xpath('//div[@class="box_705"]/div[@class="search_pager_layout_01"]//ul[@class="pager_layout_01"]/li/a/text()').extract()[-1]
        next_url = urls[-1]
        if next_index == '▶次へ':
                yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        #使用itemloadder获取信息
        item_loader = Prestige_itemloader(item=Prestige_Item(), response=response)
        #网页格式有两种，一种是有演员名字的，一种是没有演员名字的，所以做个判断
        if response.xpath("//dl[@class='spec_layout']/dt[1]/text()").extract_first() == '出演：':
            actress_xpath = response.xpath("//dl[@class='spec_layout']/dd[1]")
            actress = actress_xpath.xpath("string()").extract()
            # 获取演员名称
            item_loader.add_value("actress", actress)
            # 获取电影id
            item_loader.add_xpath("video_number", "//dl[@class='spec_layout']/dd[5]/text()")
            # 获取电影名字
            item_loader.add_xpath("video_name", "//div[@class='product_title_layout_01']/h1/text()")
            # 获取电影时长
            item_loader.add_xpath("video_lasts", "//dl[@class='spec_layout']/dd[2]/text()")
            # 获取电影发售日期
            item_loader.add_xpath("release_date", "//dl[@class='spec_layout']/dd[3]/a/text()")
        else:
            # 获取演员名称
            item_loader.add_value("actress", "未知")
            # 获取电影id
            item_loader.add_xpath("video_number", "//dl[@class='spec_layout']/dd[4]/text()")
            # 获取电影名字
            item_loader.add_xpath("video_name", "//div[@class='product_title_layout_01']/h1/text()")
            # 获取电影时长
            item_loader.add_xpath("video_lasts", "//dl[@class='spec_layout']/dd[1]/text()")
            # 获取电影发售日期
            item_loader.add_xpath("release_date", "//dl[@class='spec_layout']/dd[2]/a/text()")

        # 这是获取影片截图的xpath
        item_loader.add_xpath("image_urls", "//a[@class='sample_image']/@href")
        prestige_Item = item_loader.load_item()
        yield prestige_Item