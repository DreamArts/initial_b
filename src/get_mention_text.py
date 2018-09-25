from gremlin_python.driver import client, serializer
from dotenv import load_dotenv
import json
import os
from os.path import join, dirname

path = './existMessageGroupList.json'
existGroup = []

_dict_all = []


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
env = os.environ

with open(path) as f:
    df = json.load(f)

# 環境変数の取得
ENDPOINT = str(env.get('ENDPOINT'))
DB_NAME = str(env.get('DB_NAME'))
GRAPH_NAME = str(env.get('GRAPH_NAME'))
PRIMARY_KEY = str(env.get('PRIMARY_KEY'))

# クライアントを生成
c = client.Client('wss://{}.gremlin.cosmosdb.azure.com:443/'.format(ENDPOINT), 'g',
                username="/dbs/{0}/colls/{1}".format(DB_NAME, GRAPH_NAME),
                password="{}".format(PRIMARY_KEY),
                message_serializer=serializer.GraphSONSerializersV2d0()
                )

users_id = []

# 被メンションのあるユーザを取得
for eG in df:
    # クエリを発行してcallbackを取得
    __query = "g.V().hasLabel('group').has('id','{0}').in('belongsTo')".format(eG)
    callback = c.submitAsync(__query)
    # コールバックが複数回に分かれて返ってくるので一つのリストにする
    res = [i for it in callback.result() for i in it]

    for i in range(len(res)):
        users_id.append(res[i]['properties']['name'][0]['value'])

# 被メンションのあるユーザのユニークリストを生成    
usr_unique = list(set(users_id))

for usr in usr_unique:
    # 被メンションを受けたユーザごとのメッセージを出力するjsonファイルのpath
    path_usr = './data/' + usr + '.json'

    # メンションを受けているメッセージの取得
    __query = "g.V().hasLabel('user').has('name','{0}').in('mentions')".format(usr)
    callback = c.submitAsync(__query)
    # コールバックが複数回に分かれて返ってくるので一つのリストにする
    res = [i for it in callback.result() for i in it]


    # 以下，メッセージ辞書のリスト
    dic_list = []
    for re in res:
        text = re['properties']['text'][0]['value']
        # textがないものは省略
        if text == '':
            pass
        # textの存在するものについて，辞書を作成
        else:
            dic = {}
            dic['id'] = re['id']
            dic['text'] = text
            dic['createdAt'] = re['properties']['createdAt'][0]['value']
            dic_list.append(dic)


    __query = "g.V().hasLabel('user').has('name','{}').values('fullName')".format(usr)
    callback = c.submitAsync(__query)
    # コールバックが複数回に分かれて返ってくるので一つのリストにする
    res = [i for it in callback.result() for i in it]   

    _dic_messages = {'user' : res[0]}

    # 全てのメッセージについて，その送信者(ユニーク)と受信者(複数名の可能性)を取得
    for d in dic_list:
        # メッセージの送信者を取得
        __query = "g.V().hasLabel('message').has('id','{0}').in('posts')".format(d['id'])
        callback = c.submitAsync(__query)
        # コールバックが複数回に分かれて返ってくるので一つのリストにする
        res = [i for it in callback.result() for i in it]
        d['from'] = res[0]['properties']['fullName'][0]['value']
        if res[0]['properties']['type'][0]['value'] == 'user':
            d['isUser'] = 'True'
        else:
            d['isUser'] = 'False'

        # メッセージの受信者を取得
        __query = "g.V().hasLabel('message').has('id','{0}').out('mentions')".format(d['id'])
        callback = c.submitAsync(__query)
        # コールバックが複数回に分かれて返ってくるので一つのリストにする
        res = [i for it in callback.result() for i in it]
        li = []
        # 受信者は複数の可能性がある．
        for re in res:
            li.append(re['properties']['fullName'][0]['value'])
        d['to'] = li
        del d['id']

    _dic_messages['message'] = dic_list
    # jsonの形式で出力（ファイルは新規作成 OR 上書き）
    if len(dic_list) > 0:
        _dict_all.append(_dic_messages)
        with open(path_usr , mode = 'w') as f:
            json.dump(_dic_messages, f, indent=2 ,ensure_ascii=False)
    else:
        pass


# 全てを統合したデータ
with open('./data/all.json' , mode = 'w') as f:
    json.dump(_dict_all, f, indent=2 ,ensure_ascii=False)
