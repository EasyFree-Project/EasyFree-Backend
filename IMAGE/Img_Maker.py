import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import clear_output
import json
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from PACK import FileSearch

def check_img(FILE_PATH = '', save_pos = 0, cutoff = 240):
    for next_img in pd.read_json(FILE_PATH)[save_pos:].iloc:
        img_data = np.asarray(next_img[2]).reshape(224,224,3)
        print('이번 카테고리 :', str(next_img[0]).zfill(10))
        print('Save Point :', save_pos)
        png_data, label_map = image_trans(img_data, cutoff)
        label_img = np.asarray(label_map).reshape(224,224,-1)
        # 라벨 박스
        box_label_image = change_boundary(label_img, find_boundary(label_img))

        if len(FILE_PATH.split('/')) > 1:
            img_name = FILE_PATH.split('/')[-2:]
        if len(FILE_PATH.split('\\')) > 1:
            img_name = FILE_PATH.split('\\')[-2:]
        img_name[1] = img_name[1].split('.')[0]
        img_name = '_'.join(img_name)+'_%s'%save_pos

        print('빨간색 박스가 상품을 잘 표현한다면 1, 제대로 표현하지 못한다면 0을 입력하세요(종료는 2) : ')
        img_show(img_data, box_label_image)
        s = input()
        clear_output()
        if s == '1':
            save_img(png_data, './Trans_Image/%s'%img_name)
            save_coco('./coco_file.csv', '%s'%img_name, next_img[0], next_img[1], find_boundary(label_img))
        elif s == '2':
            print('마지막 Save Point %s'%save_pos)
            break
        save_pos += 1

# 이미지 투명화
def image_trans(img_data, cutoff):
    a, b = [], []
    for item in img_data.reshape(-1,3):
        if item[0] >= cutoff and item[1] >= cutoff and item[2] >= cutoff:
            a.append((255, 255, 255, 0))
            b.append((0,0,0))
        else:
            a.append((item[0], item[1], item[2], 255))
            b.append((255,255,255))
    return a, b

# 경계선 찾기
def find_boundary(label_map): # 224x224x3 nparray
    x_min, y_min, x_max, y_max = 224, 224, 0, 0
    for i in range(224):
        for j in range(224):
            if label_map[i][j].tolist() != [0,0,0]:
                x_min = min(x_min, i)
                x_max = max(x_max, i)
                y_min = min(y_min, j)
                y_max = max(y_max, j)
    return x_min, x_max, y_min, y_max

# 경계선 빨간색으로 변경
def change_boundary(images, boundary): # images = label_map(224x224x3) / boundary = x_min, x_max, y_min, y_max
    x_min, x_max, y_min, y_max = boundary
    for i in range(x_min, x_max):
        images[i][y_min] = (255,0,0)
        images[i][y_max] = (255,0,0)
    for j in range(y_min, y_max):
        images[x_min][j] = (255,0,0)
        images[x_max][j] = (255,0,0)
    return images

# 이미지 Plotting
def img_show(*images):
    plt.figure(figsize=(len(images)*5, 6))
    plt.imshow(np.hstack((images[0], images[1])).reshape(224, len(images)*224, 3))
    plt.show()

# coco 용 center_x, center_y, width, height 찾기
def xywh(boundary):
    x_min, x_max, y_min, y_max = boundary
    return (x_max+x_min)//2, (y_max+y_min)//2, x_max-x_min, y_max-y_min

# coco 파일에 x, y 가 이미지상 x, y좌표와 다름
def reverse_xywh(boundary):
    center_x, center_y, width, height = boundary
    return center_x - width//2, center_x + width//2, center_y - height//2, center_y + height//2

# 이미지 저장
def save_img(images, file_name):
    # 대체를 위한 투명 이미지
    img = Image.open("transparent.png")
    img.putdata(images)
    img.save("%s.png"%file_name, "PNG")

# 이미지 정보 저장
def save_coco(coco_file, file_name, category_number, product_number, boundary):
    center_x, center_y, width, height = xywh(boundary)

    data = {
            'image_name' : file_name, # Image 파일 이름
            'category' : category_number, # Target
            'product' : str(product_number).zfill(13), # 제품 번호
            'x' : center_x,
            'y' : center_y,
            'w' : width,
            'h' : height
            }
    
    insert_data = '\n'
    for i in data:
        insert_data += '%s,'%data[i]

    with open(coco_file, 'a', encoding='utf-8') as f:
        f.write(insert_data[:-1])

# 학습 이미지 생성
def mk_TrainData(FILE_PATH, FILE_NAME='et_a', FILE_COUNT=100):
    coco = pd.read_csv(FILE_PATH)
    item_list = list(coco['image_name'])
    bg_fl = FileSearch.search('./Emart_Image', '.jpg')
    item_fl = list(map(lambda i : './Trans_Image/{}.png'.format(i), item_list))
    # 이미지가 최소 한번씩은 활용되게?
    img_count = 0
    MAX_IMG = 0
    file_counter = 0
    while True:
        this_item = np.random.randint(len(item_fl))
    # for i in range(len(item_fl)):
        if img_count == MAX_IMG:
            try: bg.save("./Train_Image/%s_%s.jpg"%(FILE_NAME, file_counter))
            except: pass
            this_bg = np.random.randint(len(bg_fl))
            # bg_name = bg_fl[this_bg].split('\\')[1].split('.jpg')[0]
            bg = Image.open(bg_fl[this_bg])
            bg = bg.resize((1024,1024))
            bg_w, bg_h = 1024, 1024
            img_count = 0
            MAX_IMG = bg_w * bg_h // 40000
            file_counter += 1
            source = ['emart_1','emart_2','emart_3','emart_4','emart_5','emart_6'][np.random.randint(0,6)]
            if file_counter == FILE_COUNT+1:
                break

        img_count += 1
        category = coco.iloc[this_item]['category']

        item = Image.open(item_fl[this_item])
        item = item.resize((112,112))
        min_x, max_x, min_y, max_y = reverse_xywh(coco.iloc[this_item][['x','y','w','h']])
        min_x //= 2 
        max_x //= 2 
        min_y //= 2 
        max_y //= 2 
        w, h = coco.iloc[this_item][['w','h']]
        w //= 2 
        h //= 2

        in_x, in_y = np.random.randint(-min_y, bg_w - max_y), np.random.randint(-min_x, bg_h - max_x)
        bg.paste(item, (in_x, in_y), item)

        # coco file 작성 (이미지 좌측 위를 0,0 이라 했을 때, x - 가로, y - 세로 좌표)
        coco_data = '\n%s,%s,%s,%s,%s,%s,%s'%('%s_%s'%(FILE_NAME, file_counter), category, in_x + min_y, in_y + min_x, h, w,source) # + h // 2 + w // 2
        with open('./coco_train.csv', 'a', encoding='utf-8') as f:
            f.write(coco_data)
        
