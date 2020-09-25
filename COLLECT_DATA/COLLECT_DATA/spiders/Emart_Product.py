import scrapy
from Package import FileMaker
import pandas as pd

import urllib.request
from PIL import Image
import numpy as np
import io

from bs4 import BeautifulSoup
import re

# Target User Cralwer
class EmartSpider(scrapy.Spider):

    name = "emart"
    
    # DB FILE
    fm = FileMaker.JsonMaker('./EMART_DATA/', data_count = 50000)
    # MODEL FILE
    MF = FileMaker.JsonMaker('./MODEL_DATA/', data_count = 10000)

    # category_idx - (지영이 파일로 받기)
    category_idx = 'test'
    
    # 1000015571935 - 초코칩쿠키
    # 1000028412340 - 사과
    product_number = 1000015571935
    image_size = 600
    
    def __init__(self, TARGET_ID=''):
        self.TARGET_ID = TARGET_ID
        
    def start_requests(self):
        # 카테고리 별로 분류
        EmartSpider.fm.create_folder()
        EmartSpider.fm.write_file()

        EmartSpider.MF.create_folder()
        EmartSpider.MF.write_file()

        URL = 'http://emart.ssg.com/item/itemView.ssg?itemId=%s'%EmartSpider.product_number
        yield scrapy.Request(URL, callback= self.parse)
    
    def parse(self, response):

        # 모델 데이터 크롤링 (이미지)
        images = response.css('img.zoom_thumb::attr(src)').getall()

        # for image in images:
        #     image_data = urllib.request.urlopen('http:%s'%image.replace('84.jpg','%s.jpg'%EmartSpider.image_size)).read() # byte values of the image
        #     image = Image.open(io.BytesIO(image_data))
        #     image = image.convert('RGB')
        #     # image = image.resize((image_w, image_h))
            
        #     # numpy 배열 -> list로 변환, 이후 np.asarray().reshape(600,600,3)로 다시 형변환
        #     data = np.asarray(image).flatten().tolist()
        #     yield EmartSpider.MF.add_data({
        #             'category_id' : str(EmartSpider.category_idx),
        #             'product_id' : str(EmartSpider.product_number),
        #             'image_vec' : data
        #     })
        

        # 제품 데이터 크롤링 (텍스트)
        grades = response.css('span.cdtl_grade_num')

        th = response.css('div.ty2 th div.in::text').getall()
        td = response.css('div.ty2 td div.in::text').getall()
        for i, t in enumerate(th):
            if t == '원산지' or t == '생산자 및 소재지':
                product_location = td[i]
                continue
            if t == '포장 단위별 용량 (중량), 수량, 크기':
                capacity_size = td[i]
                continue
            if t == '주원료/함량(원료 원산지)':
                nutrient = td[i]
                continue

        # iframe
        iframe = response.css('iframe::attr(src)').getall()[1]
        # 따로 추가할 것인지
        yield scrapy.Request(url='http://emart.ssg.com%s'%iframe, callback=self.content_crawl, cb_kwargs=dict(product_number=EmartSpider.product_number))

        yield EmartSpider.fm.add_data({
            'category_idx' : EmartSpider.category_idx, # 사과, 배, 등 큰 카테고리
            'product_number' : str(EmartSpider.product_number), # 제품 번호
            'product_name' : response.css('h2.cdtl_info_tit::text').get(), # 제품 이름
            'product_price' : response.css('em.ssg_price::text').get(), # 제품 가격
            'product_location' : product_location if product_location else '', # 원산지
            'capacity_size' : capacity_size, # 중량, 등 정보
            'nutrient' : nutrient, # 성분
            'avg_review' : grades.css('em.cdtl_grade_total::text').get(), # 평점
            'review_count' : grades.css('span.num::text').get(), # 리뷰 수
            })

    def close(self, reason):
        EmartSpider.fm.close_file()
        EmartSpider.MF.close_file()
        # print('현재 카테고리 : {} 크롤링 종료'.format(self.category_idx))

    # cb_kwargs=dict(product_number=product_number)
    def content_crawl(self, response, product_number):
        soup = BeautifulSoup(response.css('div.cdtl_tmpl_cont').get(), 'html.parser')
        content = re.sub('SSG\.COM.*permission\.', '', soup.get_text(separator=' ').replace('\n',' ').replace('\t',' ').strip())
        
        yield EmartSpider.MF.add_data({
            'data' : ' '.join(content.split()) # 설명
            })
        