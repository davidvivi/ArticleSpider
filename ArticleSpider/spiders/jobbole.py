# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
import re


# 在ArticleSpider根目录下通过scrapy genspider jobbole blog.jobbole.com生成的
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页(http://blog.jobbole.com/all-posts/)中的url并交给scrapy下载后并解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """

        # 获取列表页的所有的详情页的链接
        # 属性多值匹配 <div class="post floated-thumb"> 所以.post.floated-thumb这样写
        post_nodes = response.css("#archive .post.floated-thumb .post-thumb a")

        # xpath小技巧
        # 当我们使用class来定位标签时，可以在F12中用ctrl + F 查看这个class名字是否唯一
        # Xpath路径可右键直接复制
        # 注意：因为jquery会生成额外的代码，我们在源码看到的代码和页面加载之后显示的代码可能不同，所以不要按层级一步步找，最好找到id或class来定位

        # xpath写法 属性多值匹配 如上有多个class名，contains()函数简化操作
        # post_nodes = response.xpath(
        #     '//div[@id="archive"]/div[contains(@class,"floated-thumb")]/div[@class="post-thumb"]/a')
        # Scrapy使用了Twisted(其主要对手是Tornado)异步网络框架来处理网络通讯
        for post_node in post_nodes:
            # extract():方法会把原数据的selector类型转变为列表类型
            # extract()会得到多个值，extract()[1]取第2个值
            # extract_first()得到第一个值，类型为字符串。extract_first(default='')如果没取到返回默认值
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # meta是一个字典，它的主要作用是用来传递数据的，meta = {‘key1’:value1},meta是随着Request产生时传递的，
            # 下一个函数得到的Response对象中就会有meta，即response.meta.
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        """
        提取详情页的信息
        :param response:
        :return:
        """
        # 通过xpath选择器提取相关字段
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().split("·")[
            0]
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]  # 赞
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0].strip().split(' ')[
        #     0]  # 收藏
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]  # 评论
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.xpath("//div[@class='entry']").extract()[0]

        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()  # 标签
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        # 通过css选择器提取字段
        # front_image_url = response.meta.get("front_image_url", "")  #文章封面图
        # title = response.css(".entry-header h1::text").extract()[0]
        # create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        # fav_nums = response.css(".bookmark-btn::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.css("div.entry").extract()[0]
        #
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        pass
