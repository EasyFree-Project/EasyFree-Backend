import scrapy
import json
from Package import FileMaker
import pandas as pd

# Target User Cralwer
class EmartSpider(scrapy.Spider):

    name = "emart"
    
    fm = FileMaker.JsonMaker('./EMART_DATA/', data_count = 50000)
    
    def __init__(self, TARGET_ID=''):
        self.TARGET_ID = TARGET_ID
        
    def start_requests(self):
        # 카테고리 별로 분류
        EmartSpider.fm.create_folder(self.TARGET_ID)
        EmartSpider.fm.write_file()
        yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables={"id":"%s","first":36}'%self.TARGET_ID, callback= self.parse)
    
    def parse(self, response):
        sources = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media'] #필요한 데이터

        for source in sources['edges']:
            try:
                yield InstaSpider.fm.add_data({
                    'insta_id' : str(source['node']['owner']['id']),
                    'content' : source['node']['edge_media_to_caption']['edges'][0]['node']['text'] #게시글
                    })
            except:
                pass

        end_cursor = sources['page_info']['end_cursor'] #Next Page 확인
       
        if end_cursor != None:
            yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables={"id":"%s","first":36,"after":"%s"}'%(self.TARGET_ID, end_cursor), callback=self.parse)

    def close(self, reason):
        EmartSpider.fm.close_file()
        print('Target : {} 크롤링 종료'.format(self.TARGET_ID))
