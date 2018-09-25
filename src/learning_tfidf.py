import pickle
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import time

import  tf_idf_parser


class TFIDFModel():
    def __init__(self):
        pass
    
    def tfidf(self,mesList):
        self.vectorizer = TfidfVectorizer(analyzer=tf_idf_parser.parse, 
                                    min_df=5, max_df=0.1, max_features=5000)
        self.x = self.vectorizer.fit_transform(mesList)

        return self.x , self.vectorizer
    
    def load_json(self, json_path = '../pickle/all.json'):
        self.messageList = []
        self.whole_message = []
        self.whole_id = []
        self.usr_mId_dic = {}
        with open(json_path) as f:
            self.messageList = json.load(f)
        for usr_message in self.messageList:
            for message in usr_message['message']:
                if len(message) != 0:
                    self.whole_message.append(message['text'])
                    self.whole_id.append(message['id'])
                    if not message['id'] in self.usr_mId_dic:
                        self.usr_mId_dic[message['id']] = [usr_message['user']]
                    else:
                        self.usr_mId_dic[message['id']] += [usr_message['user']]
                    

    def learning(self, tfidf_path = '../pickle/tdidf_result.pkl' 
                        , vector_path = '../pickle/vectorlizer.pkl'):

        print ('start')
        st = time.time()

        self.tfidf_result, self.vectorizer = self.tfidf(self.whole_message)
        # terms = vectorizer.get_feature_names()

        print('End {0} s'.format(time.time() - st))
        # pickleに書き込む．
        with open(tfidf_path, 'wb') as f:
            pickle.dump(self.tfidf_result, f)
        with open(vector_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def isPickleFile(self, tfidf_path = '../pickle/tdidf_result.pkl' 
                        , vector_path = '../pickle/vectorlizer.pkl' ):
        if not os.path.exists(tfidf_path) and not os.path.exists(vector_path):
            return False
        else:
            with open(vector_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(tfidf_path, 'rb') as f:
                self.tfidf_result = pickle.load(f)           

            return True
    
    def most_similar(self, _input='', num=5):
        self.load_json()
        if not self.isPickleFile():
            g = input('Learning has not finished yet. Do you wanna start Learning? (y/N)')
            if g == 'y':
                self.learning()
            else:
                pass
        else:
            end_index = -1 - num
            _cos_sim = np.copy(cosine_similarity(np.sum(self.vectorizer.transform(list(tf_idf_parser.parse(_input))),axis=0), self.tfidf_result))
            index = _cos_sim[0].argsort()[end_index:-1]
            
            return [(usr, self.whole_message[i], _cos_sim[0][i]) for i in reversed(index) for usr in self.usr_mId_dic[self.whole_id[i]] ][0:num]


def main():
    td = TFIDFModel()
    _input = input('>> ')
    print(td.most_similar(_input))



if __name__ == '__main__':
    main()





