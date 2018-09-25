import sys
import MeCab
import re
from urlextract import URLExtract

import pprint


class Parser:
    def __init__(self, s):
        self._s = s
        self._dic = {}

    def parse(self):
        mecab = MeCab.Tagger(
            '-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        res = mecab.parse(self.word_validator(self._s)).rstrip()
        keywords = res.split(' ')

        return keywords

    # 名詞だけとってくるやつ
    def parse_noun(self):
        mecab = MeCab.Tagger(
            '-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

        # 謎のバグの解決法
        # https://qiita.com/kasajei/items/0805b433f363f1dba785
        mecab.parse("")

        node = mecab.parseToNode(self.word_validator(self._s))
        keywords = []

        while node:
            meta = node.feature.split(',')

            if meta[0] == '名詞':
                keywords.append(node.surface)
            node = node.next

        return keywords

    def word_validator(self, docs, replace=''):
        extractor = URLExtract()
        urls = extractor.find_urls(docs)
        for url in urls:
            docs = docs.replace(url, '')
        docs = re.sub(
            r'[!-/]|[:-@]|[\[-`]|[\{-~]|[︰-＠]|\n|[\u3000-\u3030]', '', docs)
        return docs


def main():
    p = Parser(input())
    print(p.parse())
    print(p.parse_noun())


if __name__ == '__main__':
    main()
