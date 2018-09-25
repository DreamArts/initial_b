# Initial-B

# Start

``` sh
brew install xz mecab mecab-ipadic curl
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd
./bin/install-mecab-ipadic-neologd -n -a
pipenv install
```

# Dependencies

- python 3.6+
- cython
- word2vec
- gensim
- tensorflow
- mecab-python3
- flask
- gunicorn
- python-dotenv
- request
- urlextract
- numpy
- scikit-learn 

- neologd

# neologd関連

[neologd/mecab-ipadic-neologd/blob/master/README.ja.md](https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md)

# ディレクトリ構造

- src
- data(ここにjson群を入れとく)
- model(ここにdoc2vec.model置いとく)
- mecab-ipadic-neologd

# 学習済みデータとか

https://drive.google.com/drive/folders/18jrJKt2F1FAXAs13zQU97N-9vRyiNwcZ
