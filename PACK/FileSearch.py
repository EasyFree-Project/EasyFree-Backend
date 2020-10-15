import os

# 현재 경로 확인 필수

# 파일 검색 (폴더명 혹은 전체탐색 시 .)
def search(dirname, file_type='.json'):
    filenames = os.listdir(dirname)
    fl = []
    for filename in filenames:
        if file_type in filename:
            fl.append(os.path.join(dirname, filename))
    return fl

# 파일 이름 변경
def name_change(file_path, file_type, target_name):
    i = 1
    for name in search(file_path, file_type):
        os.rename(name, os.path.join(file_path, '%s_%s%s'%(target_name, i, file_type)))
        i += 1

# name_change('./Emart_Image', '.jpg', 'emart_display')

# 파일 삭제
# os.remove(path, option)
# 디렉토리 삭제
# os.rmdir(path, option)