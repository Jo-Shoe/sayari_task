import scrapy
import json


class ND_spider(scrapy.Spider):
    '''Queries the North Dakota Secy of State Business Search page and copies resulting info into JSON file. Expected usage:
                    $ scrapy runspider nd_spider.py -a query=<str> -s FEED_URI=<filepath> '''
    name = "ND_business_search"
    custom_settings = {"FEED_FORMAT": "jsonlines"}

    def __init__(self, *args, **kwargs):
        super(ND_spider, self).__init__(*args, **kwargs)
        self.query = kwargs.get("query", "X")

    def start_requests(self):
        url = "https://firststop.sos.nd.gov/api/Records/businesssearch"
        return [scrapy.http.JsonRequest(url,
                                        data={
                                            "SEARCH_VALUE": self.query, "STARTS_WITH_YN": True, "ACTIVE_ONLY_YN": True},
                                        callback=self.select_IDs)]

    def select_IDs(self, resp):
        result = json.loads(resp.body)
        biz_ids = dict()
        qlen = len(self.query)
        lowered = self.query.lower()
        for biz_id, biz_dict in result.get("rows", dict()).items():
            name = biz_dict.get("TITLE", ("", ""))[0]
            status = biz_dict.get("STATUS", "Inactive").lower()
            if name[:qlen].lower() == lowered and status == "active":
                biz_ids[biz_id] = name
        for biz_id, biz_name in biz_ids.items():
            yield scrapy.Request("https://firststop.sos.nd.gov/api/FilingDetail/business/%s/false" % biz_id,
                                 callback=self.parse,
                                 cb_kwargs={"biz_name": biz_name})

    def parse(self, resp, biz_name=None):
        biz_dict = {"Name": biz_name}
        biz_data = resp.xpath("//DRAWER_DETAIL")
        biz_dict.update({item.xpath("string(./LABEL/text())").get(): item.xpath("string(./VALUE/text())").get() for item in biz_data})
        return biz_dict
