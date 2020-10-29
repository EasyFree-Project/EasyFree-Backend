 # -*- coding: utf-8 -*-
import pickle
import numpy as np
from konlpy.tag import Mecab
import sys

class predict_region:

    def _tokenize(self, doc):
        mecab = Mecab()
        tokens = mecab.morphs(doc)

        return tokens


    def _feature_vector(self, key_terms, tokens):
        feature_vec = []

        for term in key_terms:
            if term in tokens:
                feature_vec.append(1)
            else:
                feature_vec.append(0)

        return feature_vec


    def predict(self, doc):
        tokens = self._tokenize(doc)
        region_dic = {'sd': '수도권', 'gs': '경상', 'gw': '강원', 'cc': '충청', 'jl': '전라'}
        region = 'none'
        tmp = 0

        for i in region_dic.keys():
            # key terms 
            with open('C:/Users/ehhah/dev/NLP_workspace/EasyFree/EasyFree-Backend/SERVER/EasyFree/key_terms/region_{}_words.txt'.format(i), 'rb') as f:
                key_terms = pickle.load(f)

            # load models
            with open('C:/Users/ehhah/dev/NLP_workspace/EasyFree/EasyFree-Backend/SERVER/EasyFree/models/region_{}_model.bin'.format(i), 'rb') as f:
                model = pickle.load(f)

            # predict
            feature_vec = self._feature_vector(key_terms, tokens)
            feature_vec = np.reshape(feature_vec, (1, -1))

            prob = model.predict_proba(feature_vec)[0][1]
            if prob > tmp:
                tmp = prob
                region = i

        print(region_dic[region])


# run
p = predict_region()
p.predict(sys.argv[1])





