import ngtpy
import random
import argparse
import pickle
import torch
import time
from tqdm import tqdm
import os
import json
def _read_json(input_file):
    """Reads a tab separated value file."""
    with open(input_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        return json.loads(content)
def generate_dir_files(db_dir_path):
    return [os.path.join(db_dir_path, f) for f in os.listdir(db_dir_path)]
import sys
def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)
import sys
from itertools import permutations
import logging
logger = logging.getLogger(__name__)
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import nltk
import itertools
from whoosh.analysis import FancyAnalyzer
def CleanQE(keyword,qelist,vocablist,ps):
    keywords = keyword.split()
    new_keywords = [w for w in keywords if not w in stop_words]
    new_qewords = [w for w in qelist if not w in stop_words]
    keyword_in_vocab = []
    for word in new_keywords:
        word = word.lower()
        if word in vocablist:
            keyword_in_vocab.append(word)
    if len(keyword_in_vocab)!=0:
        new_qewords = [" ".join(keyword_in_vocab)]+new_qewords
    output_keywords = []
    stem_qewords = []
    ana = FancyAnalyzer()
    for word in new_qewords:
        word = " ".join([token.text for token in ana(word)])
        stem_word = ps.stem(word)
        if stem_word not in stem_qewords:
            output_keywords.append(word)
            stem_qewords.append(stem_word)
    return output_keywords
def CleanWordQE(word,qe_score_list,vocablist,ps):
    max_score = qe_score_list[0][1]
    if word in stop_words:
        return []
    else:
        stem_qewords = []
        new_qe_score_list = []
        if word not in stop_words and word in vocablist:
            new_qe_score_list.append((word, max_score))
            stem_qewords.append(ps.stem(word))
        for (qeword,score) in qe_score_list:
            if qeword not in stop_words:
                if ps.stem(qeword) not in stem_qewords:
                    new_qe_score_list.append((qeword,score))
                    stem_qewords.append(ps.stem(qeword))
        return new_qe_score_list

def is_all_eng(strs):
    import string
    for i in strs:
        if i not in string.ascii_lowercase+string.ascii_uppercase:
            return False
    return True
if __name__ == '__main__':
    dir = "Lexical_XEL/WordIndex"
    index_dir = "{}/Index".format(dir)
    index_uri_id_file = "{}/index_words.pk".format(index_dir)
    is_NMS = True
    data_dir = "Lexical_XEL/DBVecIndex/qaldv3"
    #------------------------------------------------------------
    lan_dict = {
        'en': 'english', 'de': 'german', 'fr': 'french', 'ru': 'russian', 'nl': 'dutch',
        'es': 'spanish', 'it': 'italian', 'ro': 'romanian', 'pt': 'portuguese'
    }
    test_files = []
    for lan in ['de','fr','ru','es','it','nl','ro','pt']:
        qald_file = "{}/qald_{}.pk".format(data_dir,lan)
        output_qald = "{}/qald_{}_qe.pk".format(data_dir,lan)
        ps = nltk.stem.SnowballStemmer(lan_dict[lan])
        ps_en = nltk.stem.SnowballStemmer(lan_dict['en'])
        dataset_uris = []
        all_data = pickle.load(open(qald_file, 'rb'))
        for data in tqdm(all_data):
            keyword2SearchResult = {}
            for keyword,wordep in data['query2epandword'].items():
                expand_list = []
                for (word, expands) in wordep:
                    if is_NMS:
                        new_expandwords = CleanWordQE(word,expands[0:30],DB_vocab_list,ps_en)
                        if len(new_expandwords)!=0:
                            expand_list.append(new_expandwords)
                if len(expand_list) == 1:
                    keyword2SearchResult[keyword] = expand_list[0][0:20]
                else:
                    if len(expand_list) <6:# if the mention contains too many words, word_n should be smalle
                        word_n = 10
                    else:
                        word_n = 5
                    epwords_list = []
                    scores_list = []
                    for aitem in expand_list:
                        temp = list(zip(*aitem[0:word_n]))
                        if len(temp) == 0:
                            print("!")
                        epwords_list.append(list(temp[0]))
                        scores_list.append(list(temp[1]))
                    combined_words = list(itertools.product(*epwords_list))
                    combined_scores = list(itertools.product(*scores_list))
                    Final_combined_list = []
                    for idx,(c_w,c_s) in enumerate(list(zip(combined_words,combined_scores))):
                        if len(c_s)!=0:
                            c_word = " ".join(list(c_w))
                            c_score = sum(c_s)/len(c_s)
                            Final_combined_list.append((c_word,c_score))
                    #-----------------
                    combined_list = sorted(Final_combined_list, key=lambda x: x[1], reverse=True)[0:20]

                    keyword2SearchResult[keyword] = combined_list

            data["plau_words"] = keyword2SearchResult
        pickle.dump(all_data,open(output_qald,'wb'))
        print(output_qald)
