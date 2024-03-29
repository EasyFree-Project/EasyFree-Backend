# [EasyFree] Object Detection을 이용한 핸드프리 쇼핑 앱

**2020 인공지능을 활용한 자연어처리과정 Final Project**

------

#### 프로젝트 개요

기업이 온라인을 통해 축적한 기술이나 데이터를 상품 조달 등에 적용해 오프라인으로 사업을 확대하는 신규 Biz 플랫폼, Online for Offline(O4O)

> SLOGAN : Easy &Fun shopping, Hands Free (Easy Free)

오프라인에서는 쇼핑하는 재미를, 온라인에서는 고객의 불편을 해소하는 EasyFree 제안

![logo](./src/img/logo.png)

#### 프로젝트 목표

‘Object Detection’을 활용하여 모바일에서 제품 리스트, 원산지, 성분 정보를 확인하고 주문을 처리할 수 있는 쇼핑 앱 개발

#### 활용방안 & 기대효과

![effect](./src/img/effect.png)

1. 고객이 장바구니를 들고 직접 물건을 가지고 가야하는 불편 해소
2. 고객에게 제품 정보나 연관 물품을 스마트폰으로 제공
3. 고객 구매 데이터를 수집, 분석, 마케팅에 활용
4. QR 코드를 통한 제품 인식 가능

------

### Project Download

```
git clone 'https://github.com/EasyFree-Project/EasyFree-Backend.git'
```


### 0. Download Package

```
pip install -r requirements.txt
```


### 1. SSG E-mart Crawling

#### 1.1 Scrapy 디렉토리로 이동

```
cd EasyFree-Backend/COLLECT_DATA
```

#### 1.2 Scrapy Spider 크롤러 동작 명령어

```
scrapy crawl emart
```


### 2. Object Detection Modeling

#### 2.0 이미지 구축 방법론

이미지 구축 방법론으론 2가지를 고려함.
1. LabelImg를 활용한 이미지 라벨링 수작업
2. Google Deeplab V3+ Semantic Labeling Idea를 활용한 투명화

**2번째 구축 방법론을 활용**

- 구글 Semantic labeling Idea
![google_semantic](./src/img/google_semantic.png)

- 이미지 투명화 → 임시 이미지에 합성, Annotation 데이터 입력
![labeling_idea](./src/img/labeling_idea.png)


#### 2.1 MnasNet

![mnasnet](./src/img/mnasnet.png)

- 상품단위 예측을 위해 MnasNet 사용
- Y = accuracy & latency(지연시간, 연산시간) 
- 가벼운 데 반해 많은 Layer로 성능 향상

※ 하지만 사용하지 않음


#### 2.2 DETR

![detr](./src/img/detr.png)
- Facebook AI Developer + PyTorch ▶ Object Detection
- Backbone – CNN(RESNET50, RESNET101), 이미지 Feature 추출
- Transformer Encoder, Decoder - Object Box 예측

- RESNET50 기준 모델 용량 158MB

![train_1](./src/img/train_image_1.png)

Object 크기를 고려하지 않고 검증하면,

![valid_1](./src/img/valid_image_1.png)

다음과 같이 학습된 환경 하 검증은 잘 됨.
하지만 실제 이미지로 검증 시, 크기에 따라 정확도가 현저히 떨어지는 모습을 보임

![train_2](./src/img/train_image_2.png)

따라서 Object 크기를 랜덤하게하여 Object Box 크기도 학습

![emart_image](./src/img/emart_image.png)

그 결과, 다음과 같이 학습되지 않은 환경 하 검증도 높은 수준으로 검증을 하게 됨

### 3. Database

#### 3.1 Entity Relation Diagram

![EasyFree_erd](https://user-images.githubusercontent.com/30308916/99019542-dd6f0380-259f-11eb-9415-39e7b23a9517.PNG)



### 4. Server (API)

#### 4.0 설치 모듈과 주소

##### 설치 모듈
```
express, express-session, mysql, express-mysql-session, http, body-parser, pbkdf2-password, python-shell,
moment, moment-timezone, multer, path
```

##### 주소
```
http://54.180.153.44:3003
http://220.87.55.135:3003
```

#### 4.1 input

##### POST
```
Content-Type: application/json 형식

로그인 : username, password
회원가입 : username, password, displayName
구매(장바구니) : member_idx, data(product_number, product_count)

multipart/form-data 형식(form-data 형식)
모델실행 : productImg
```

##### GET
```
상품검색 : ~/product/:category_number
```

#### 4.2 output

```
Content-Type: application/json 형식
return message : statusCode, message
```



> Reference
>
> 1. [Notion](https://www.notion.so/EasyFree-046515e567a74555b929ca4168579e16)
> 2. GitHub ([Android](https://github.com/EasyFree-Project/EasyFree-Android), [iOS](https://github.com/EasyFree-Project/EasyFree-iOS), [Backend](https://github.com/EasyFree-Project/EasyFree-Backend))
> 3. [Application (Playstore)](https://play.google.com/store/apps/details?id=com.sosin.easyfree)
> 4. [최종 보고서](https://drive.google.com/file/d/1pS-XlnIR-GEnt_eicvVs0ndYX__znosm/view?usp=sharing)
