import os
import json
from learning import Doc2VecModel
from learning_tfidf import TFIDFModel
from chiwawa_client import ChiwawaClient

from flask import Flask, request
from dotenv import load_dotenv

from collections import defaultdict

app = Flask(__name__)
load_dotenv('.env')
env = os.environ


@app.route('/message', methods=['POST'])
def messages():
    if is_request_valid(request):
        body = request.get_json(silent=True)
        company_id = body['companyId']
        msg_obj = body['message']
        group_id = msg_obj['groupId']
        message_text = msg_obj['text']
        user_name = msg_obj['createdUserName']

        # ChiwawaClientを起動
        cc = ChiwawaClient(company_id, env['CHIWAWA_API_TOKEN'])

        d_model = Doc2VecModel('../model/doc2vec_v2.model')

        print('hoge')
        vec = d_model.infer_vector(message_text)
        doc2vec_most = d_model.most_similar(vec, 100)

        t_model = TFIDFModel()
        tfidf_most = t_model.most_similar(message_text, 100)

        merge_list = merge(doc2vec_most, tfidf_most)
        with open('../real_data/maskedFullNameToOriginName.json') as f:
            mFN2FN_Dic = json.load(f)

        for name, message, similarity in merge_list[:5]:
            cc.post_message(
                group_id, '{0}さんとの類似度 -> {1}, message -> {2}'.format(mFN2FN_Dic[name], similarity, message))
        
        men = ''
        for i in range(5):
            men += '@{0}: '.format(mFN2FN_Dic[merge_list[i][0]])

        cc.post_message(
            group_id, '@mention予測候補', attachments=[
                {
                    "attachmentId": "u001",
                    "viewType": "text",
                                "title": "@mention候補",
                                "text": men
                }
            ])
        return "OK"
    else:
        return "Request is not valid."


def merge(doc2vec_list: list, tfidf_list: list):
    all_dic = {}
    for tag, sim in doc2vec_list:
        name, file_name, index = tag.split('-')
        dic = {}
        with open(file_name, 'r') as f:
            dic = json.load(f)
        all_dic[(name, dic['message'][int(index)]['text'])] = [sim, 0.0]

    for name, message, sim in tfidf_list:
        if (name, message) not in all_dic:
            continue
        all_dic[(name, message)][1] = sim

    ret = []
    for key, value in all_dic.items():
        name, message = key
        doc2vec_sim, tfidf_sim = value
        if doc2vec_sim == 0.0 or tfidf_sim == 0.0:
            continue
        ret.append((name, message, max(doc2vec_sim, tfidf_sim)))

    ret = sorted(ret, key=lambda sim: sim[2], reverse=True)
    return ret


# Check if token is valid.


def is_request_valid(request):
    validationToken = env['CHIWAWA_VALIDATION_TOKEN']
    requestToken = request.headers['X-Chiwawa-Webhook-Token']
    return validationToken == requestToken
