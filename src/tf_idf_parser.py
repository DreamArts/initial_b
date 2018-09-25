import sys
import MeCab
import re
from urlextract import URLExtract

import pprint

mecab = MeCab.Tagger(
    '-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

def parse(s):
    keywords = []
    if type(s) == list:
        for i in range(len(s)):
            mecab.parse("")
            res = mecab.parseToNode(word_validator(s[i]))
            keyword = []
            while res:
                meta = res.feature.split(',')
                if meta[0] == '名詞':
                    keyword.append(res.surface)
                elif meta[0] == '形容詞':
                    keyword.append(res.surface)
                res = res.next
            keywords.append(keyword)
    else:
        mecab.parse("")

        res = mecab.parseToNode(word_validator(s))

        while res:
            meta = res.feature.split(',')
            if meta[0] == '名詞':
                keywords.append(res.surface)
            elif meta[0] == '形容詞':
                keywords.append(res.surface)
            res = res.next
        

        return keywords
        

def word_validator(docs, replace='URL'):
    extractor = URLExtract()
    urls = extractor.find_urls(docs)
    for url in urls:
        docs =  docs.replace(url,replace)
        
    # docs = re.sub(r'[︰-＠]|\n|[\u3000-\u3030]', "", docs)
  
    return docs


def main():
    p = 'http://google.co.jp はダメなんですか．'
    print(parse(p))


if __name__ == '__main__':
    main()