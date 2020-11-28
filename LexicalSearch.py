from whoosh.qparser import QueryParser
from whoosh.fields import *
from whoosh.index import create_in,open_dir
import pickle
from tqdm import tqdm
from whoosh import scoring
from whoosh.analysis import StemmingAnalyzer,RegexTokenizer,LowercaseFilter,StopFilter,FancyAnalyzer
from whoosh import qparser
import timeout_decorator
import json

def _read_json(input_file):
    """Reads a tab separated value file."""
    with open(input_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        return json.loads(content)
@timeout_decorator.timeout(5, use_signals=True)
def SearchQuery(searcher,query,TopN):
    results=[]
    try:
        results = searcher.search(query, limit=TopN)
        return results
    except:
        print("ignore:",query)
        pass
    return results
def ComputeRecall(QALD_dict):
    right_examples = 0
    label_uri_count = 0
    right_uri_count = 0
    find_uri_count = 0
    for id,info in tqdm(QALD_dict.items()):
        label_uri_count+=len(info['uri'])
        Flag = True
        total_uri = []
        for hit in info['search_result']:
            total_uri.extend(hit[1].split(" "))
        total_uri = list(set(total_uri))
        find_uri_count+=len(total_uri)
        for uri in info['uri']:
            if uri not in total_uri:
                Flag = False
            else:
                right_uri_count+=1
        if Flag:
            right_examples+=1
    pre = right_uri_count/find_uri_count
    recall = right_uri_count/label_uri_count
    f1 = 2*pre*recall/(pre+recall)
    print(pre,recall,f1)
    return (pre,recall,f1)
import sys
import os
import torch
if __name__ == '__main__':
    Score = "bm25"  # bm25, tfidf, tf
    Pivots_N = 5    # number of plausible English mentions
    Search_N = 500  # number of searched entities for each plausible English mention

    InputIndexDir = "data_process/DBIndex"
    data_dir = "QALd_XEL/"
    output_dir = "Output/"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if Score == "bm25":
        myscore = scoring.BM25F()
    elif Score =="tfidf":
        myscore = scoring.TF_IDF()
    elif Score == "tf":
        myscore = scoring.Frequency()
    elif Score == "multi":
        myscore = scoring.MultiWeighting(scoring.BM25F(), id=scoring.Frequency(), keys=scoring.TF_IDF())
    else:
        myscore = scoring.BM25F()

    #---------------Input Query----------------------
    schema = Schema(title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                    content=TEXT(stored=True))
    All_Result = []
    ix = open_dir(InputIndexDir)
    sf = torch.nn.Softmax(dim=0)
    for lan in ['de','fr','ru','es','it','nl','ro','pt']:
        infile = "{}/qald_{}.pk".format(data_dir,lan)
        outfile = "{}/qald_{}_xel.pk".format(output_dir,lan)
        QALD_list = pickle.load(open(infile,'rb'))
        with ix.searcher(weighting=myscore) as searcher:
            parser = QueryParser("title", ix.schema,group=qparser.OrGroup)
            for item in tqdm(QALD_list):
                searched_uris = []
                new_item = {}
                for keyword,pwords in item['plau_words'].items():
                    per_uris = []
                    per_search_result =[]
                    for (word, score) in pwords[0:Pivots_N]:
                        query = parser.parse(word)
                        results = SearchQuery(searcher, query, Search_N)

                        hit_score = [hit.score for hit in results]
                        new_score = sf(torch.Tensor(hit_score)).tolist()
                        new_score = [score * s for s in new_score]
                        hit_title = [hit['title'] for hit in results]
                        hit_content = [hit['content'] for hit in results]
                        per_search_result.extend(list(zip(hit_title, hit_content, new_score)))
                    for c_result in per_search_result:
                        for auri in c_result[1].split(" "):
                            per_uris.append((auri, c_result[2]))
                    new_searched = sorted(per_uris, key=lambda x: x[1], reverse=True)[0:1000]
                    searched_uris.extend([item[0] for item in new_searched])
                    output_search_result[keyword] = new_searched
                item['xel_results'] = output_search_result
        pickle.dump(QALD_list,open(outfile,'wb'))