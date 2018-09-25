from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
import json
from pathlib import Path

from word_parser import Parser

import time
from multiprocessing import Pool

import logging
from logging import getLogger, StreamHandler, Formatter

logger = getLogger('Log')
logger.setLevel(logging.DEBUG)

stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)

handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(handler_format)

logger.addHandler(stream_handler)



class Doc2VecModel:
    def __init__(self, path: str = ''):
        self._model = Doc2Vec.load(path) if path != '' else None
        self._corpus = []

    # 学習
    def train(self):
        # DBoW-STS
        model = Doc2Vec(documents=self._corpus,
                        dm=0, vector_size=300, window=15, alpha=0.025,
                        min_alpha=0.025, min_count=1, sample=1e-4, negative=5)

        '''
        model = Doc2Vec(documents=self._corpus,
                        dm=1, vector_size=300, window=15, alpha=0.025, min_alpha=0.025, min_count=1, sample=1e-6)
        model.train(self._corpus,
                    total_examples=model.corpus_count, epochs=1000)
        '''

        model.train(self._corpus,
                    total_examples=model.corpus_count, epochs=400)
        self._model = model
        self._corpus = []

    def add(self, name: str, file_name, words_list):
        for i, words in enumerate(words_list):
            self._corpus.append(TaggedDocument(
                words=words, tags=['{0}-{1}-{2}'.format(name, file_name, i)]))

    # モデルの保存
    def save(self, path: str):
        self._model.save(path)

    # モデルの読み込み
    def load(self, path: str):
        self._model = Doc2Vec.load(path)

    # 近傍探索
    def most_similar(self, vec, topn=10):
        return self._model.docvecs.most_similar(vec, topn=topn)

    def infer_vector(self, s: str):
        return [self._model.infer_vector(Parser(s).parse_noun())]

def add(file_name, dic, lis, i):
    logger.debug("{0} / {1}, {2}({3})".format(i, len(lis), dic['user'], file_name))
    words_list = []
    for s in dic['message']:
        words = []
        ps = Parser(s['text'])
        # for word in ps.parse():
        for word in ps.parse_noun():
            words.append(word)

        if len(words) == 0:
            continue

        words_list.append(words)

    logger.debug('len(words_list) = {0}...'.format(len(words_list)))
    if len(words_list) == 0:
        return []

    return words_list


def main():
    g = input('>> ')

    st = time.time()

    if g == '1':
        dm = Doc2VecModel()

        p = Path('../data/')

        lis = list(p.glob('*'))

        pool = Pool(10)
        multi_res = []
        for i, file_name in enumerate(lis):
            if file_name == '../data/all.json':
                continue
            dic = {}
            with open(file_name, 'r') as f:
                dic = json.load(f)

            multi_res.append((pool.apply_async(add, (file_name, dic, lis, i)), file_name))

        for res, file_name in multi_res:
            dic = {}
            with open(file_name, 'r') as f:
                dic = json.load(f)

            words_list = res.get()
            if len(words_list) == 0:
                continue
            dm.add(dic['user'], file_name, words_list)


        logger.debug('End {0} s(parse)'.format(time.time() - st))
        dm.train()
        logger.debug('End {0} s'.format(time.time() - st))
        dm.save('../model/doc2vec_v4.model')
    else:
        s = input('>> ')
        dm = Doc2VecModel('../model/doc2vec_v4.model')
        vec = dm.infer_vector(s)
        for key, value in dm.most_similar(vec):
            dic = {}
            with open(key.split('-')[1], 'r') as f:
                dic = json.load(f)

            print(dic['user'], dic['message']
                  [int(key.split('-')[2])]['text'], value)


if __name__ == '__main__':
    main()
