import scrapy
from Package import FileMaker
from Package import Python2DB

import pandas as pd

import urllib.request
from PIL import Image
import numpy as np
import io

from bs4 import BeautifulSoup
import re

def cleanText(readData):
    #텍스트에 포함되어 있는 특수 문자 제거
    return re.sub('[-=+,#/\?:^$@*\"※~&%_ㆍ!』\\‘|\(\)\<\>`\'…》]', ' ', readData)

# Target User Cralwer
class EmartSpider(scrapy.Spider):

    name = "emart"
    
    # DB FILE
    DF = FileMaker.JsonMaker('./EMART_DATA/', data_count = 10000)
    # CONTENT FILE
    CF = FileMaker.JsonMaker('./CONTENT_DATA/', data_count = 10000)
    
    # MODEL FILE (IMAGE), 파일당 약 1GB (예상)
    MF = FileMaker.JsonMaker('D:/MODEL_DATA/', data_count = 1000)
    image_size = 224 # 일단 저장해보고 수정 (대체로 224x224를 씀)

    # ERROR FILE
    EF = FileMaker.JsonMaker('./ERROR_DATA/', data_count = 50000)

    EasyFree_DB = Python2DB


    # 파일 read 카테고리 리스트
    # CATEGORY_FILE = pd.read_csv('./emart_category.csv', index_col=0)
    # category_number = list(map(lambda i : str(i).zfill(10), CATEGORY_FILE['category_number']))

    # DB에서 카테고리 리스트 읽기
    CATEGORY_FILE = pd.DataFrame(EasyFree_DB.select('Category', '*'))
    CATEGORY_LIST = CATEGORY_FILE[0]
    CATEGORY_NAME = CATEGORY_FILE[1]
    category_idx = 0
    
    # index 맨 마지막 파일에서 받는 코드 필요
    category_idx = list(CATEGORY_LIST).index('0006510321') + 1
    
    page_number = 1

    def __init__(self, TARGET_ID=''):
        self.TARGET_ID = TARGET_ID

    def start_requests(self):
        EmartSpider.DF.create_folder()
        EmartSpider.DF.write_file()

        EmartSpider.CF.create_folder()
        EmartSpider.CF.write_file()

        EmartSpider.MF.create_folder()
        EmartSpider.MF.write_file()

        EmartSpider.EF.create_folder()
        EmartSpider.EF.write_file()

        # 크롤링 시작
        print('크롤링 시작')
        print('현재 카테고리 : %s'%EmartSpider.CATEGORY_NAME[EmartSpider.category_idx])

        # 카테고리 크롤링
        URL = 'http://emart.ssg.com/disp/category.ssg?dispCtgId=%s&page=%s'%(EmartSpider.CATEGORY_LIST[EmartSpider.category_idx], EmartSpider.page_number)
        category_num = EmartSpider.CATEGORY_LIST[EmartSpider.category_idx]
        yield scrapy.Request(URL, callback= self.category_crawl, cb_kwargs=dict(category_num=category_num))

    def category_crawl(self, response, category_num):
        # Product Number
        products = response.css('ul.cunit_thmb_lst li.cunit_t232 div.thmb > a')

        if products:
            for product in products:
                product_number = re.search('(?<=data\=\')[0-9]+', str(product.css('::attr(data-info)'))).group()
                yield scrapy.Request(url='http://emart.ssg.com/item/itemView.ssg?itemId=%s'%product_number, 
                                        callback=self.parse,
                                        cb_kwargs=dict(product_number=product_number, category_num=category_num))
            EmartSpider.page_number += 1
            print('현재 카테고리 : %s, 페이지번호 : %s'%(EmartSpider.CATEGORY_NAME[EmartSpider.category_idx], EmartSpider.page_number))
        else:
            # 파일넘버 넘기기 카테고리 리스트 URL 번호
            EmartSpider.category_idx += 1
            EmartSpider.page_number = 1
            category_num = EmartSpider.CATEGORY_LIST[EmartSpider.category_idx]
            print('다음 카테고리 : %s'%EmartSpider.CATEGORY_NAME[EmartSpider.category_idx])

        NEXT_URL = 'http://emart.ssg.com/disp/category.ssg?dispCtgId=%s&page=%s'%(EmartSpider.CATEGORY_LIST[EmartSpider.category_idx], EmartSpider.page_number)
        yield scrapy.Request(url=NEXT_URL, callback=self.category_crawl, cb_kwargs=dict(category_num=category_num))
            
    
    def parse(self, response, category_num, product_number):

        # 신규 마케팅 상품 제외 (패키지 상품)
        if not response.css('div.ty2'):
            yield EmartSpider.EF.add_data({
                'product_number' : str(product_number), # 제품 번호
                })
            return

        # 모델 데이터 크롤링 (이미지)
        images = response.css('img.zoom_thumb::attr(src)').getall()

        for image in images:
            image_data = urllib.request.urlopen('http:%s'%image.replace('84.jpg','%s.jpg'%EmartSpider.image_size)).read() # byte values of the image
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            # image = image.resize((image_w, image_h))
            # numpy 배열 -> list로 변환, 이후 np.asarray().reshape(image_size,image_size,3)로 다시 형변환
            data = np.asarray(image).flatten().tolist()
            yield EmartSpider.MF.add_data({
                    'category_number' : str(category_num),
                    'product_id' : str(product_number),
                    'image_vec' : data
            })
        

        # 제품 평점
        grades = response.css('span.cdtl_grade_num')

        # 제품상세정보 테이블
        th = response.css('div.ty2 th div.in::text').getall()
        td = response.css('div.ty2 td div.in::text').getall()

        product_location = []
        capacity_size = []
        nutrient = []
        for i, t in enumerate(th):
            if t == '원산지' or t == '생산자 및 소재지' or t == '생산자' or t == '제조국':
                product_location.append(cleanText(td[i]))
                continue
            if t == '포장 단위별 용량 (중량), 수량, 크기' or t =='용량 및 중량':
                capacity_size.append(cleanText(td[i]))
                continue
            if t == '주원료/함량(원료 원산지)' or t == '전성분':
                nutrient.append(cleanText(td[i]))
        
        # 제품 정보 DB 저장, 파일 저장
        yield EmartSpider.EasyFree_DB.insert('Product','product_number, product_name, product_content, producer_location, capacity_size, nutrient, product_price, avg_review, review_count, category_number',
                                    # "'%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, '%s'"%(
                                    '"{}", "{}", "{}", "{}", "{}", "{}", {}, {}, {}, "{}"'.format(
                                    str(product_number), 
                                    cleanText(str(response.css('h2.cdtl_info_tit::text').get()))[:45],
                                    'temp',
                                    '. '.join(product_location)[:45],
                                    '. '.join(capacity_size)[:45],
                                    '. '.join(nutrient)[:45],
                                    int(response.css('em.ssg_price::text').get().replace(',','')), 
                                    0 if len(grades.css('::text'))==0 else str(grades.css('em.cdtl_grade_total::text').get()),
                                    0 if len(grades.css('::text'))==0 else int(grades.css('span.num::text').get().replace(',','')), 
                                    category_num
                                ))

        yield EmartSpider.DF.add_data({
                                'category_number' : category_num, # 사과, 배, 등 큰 카테고리
                                'product_number' : str(product_number), # 제품 번호
                                'product_name' : response.css('h2.cdtl_info_tit::text').get(), # 제품 이름
                                'product_price' : response.css('em.ssg_price::text').get(), # 제품 가격
                                'product_location' : ', '.join(product_location), # 원산지
                                'capacity_size' : ', '.join(capacity_size), # 중량, 등 정보
                                'nutrient' : ', '.join(nutrient), # 성분
                                'avg_review' : grades.css('em.cdtl_grade_total::text').get(), # 평점
                                'review_count' : grades.css('span.num::text').get(), # 리뷰 수
                                })

        # 제품 상세 설명 iframe
        iframe = response.css('iframe::attr(src)').getall()[1]
        yield scrapy.Request(url='http://emart.ssg.com%s'%iframe, callback=self.content_crawl, cb_kwargs=dict(product_number=product_number))


    def close(self, reason):
        EmartSpider.DF.close_file()
        EmartSpider.CF.close_file()
        EmartSpider.MF.close_file()
        EmartSpider.EF.close_file()
        print('크롤링 완료')

    def content_crawl(self, response, product_number):
        try:
            soup = BeautifulSoup(response.css('div.cdtl_tmpl_cont').get(), 'html.parser')
            content = re.sub('SSG\.COM.*permission\.', '', soup.get_text(separator=' ').replace('\n',' ').replace('\t',' ').strip())
        except:
            content = ' '

        # 제품 상세 정보 DB 저장, 파일 저장
        yield EmartSpider.EasyFree_DB.update('Product', 'product_content = "{}"'.format(' '.join(content.split())[:1000]), "product_number = {}".format(str(product_number)))

        yield EmartSpider.CF.add_data({
            'product_number' : str(product_number),
            'data' : ' '.join(content.split()) # 설명
            })
    