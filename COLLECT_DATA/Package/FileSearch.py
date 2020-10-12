import os

# 파일 검색 (폴더명 혹은 전체탐색 시 .)
# 현재 경로 확인 필수
def search(dirname, file_type='.json'):
    filenames = os.listdir(dirname)
    fl = []
    for filename in filenames:
        if file_type in filename:
            fl.append(os.path.join(dirname, filename))
    return fl
