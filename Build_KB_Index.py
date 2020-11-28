import json
def read_json(input_file):
    """Reads a tab separated value file."""
    with open(input_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        return json.loads(content)
import pickle
from whoosh.analysis import FancyAnalyzer
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer,FancyAnalyzer
from tqdm import tqdm
import os
import pickle
import os
if __name__ == '__main__':

    uri2mention_file = "clean_kb_data/uri2mention_dis.pk"

    output_cleaned_mention2uri_file = "clean_kb_data/new_mention2uri.pk"
    output_DBindex_dir = "DBIndex"

    if os.path.exists(output_cleaned_mention2uri_file):
        mention2uri = pickle.load(open(output_cleaned_mention2uri_file, 'rb'))
    else:
        my_analyzer = FancyAnalyzer()
        uri_2_mention = pickle.load(open(uri2mention_file,'rb'))

        mention2uri = {}
        for uri in uri_2_mention.keys():
            alias = uri.split("/")[-1][0:-1]
            if 'Category:' in alias:
                alias = alias.split("Category:")[-1]
            mention = " ".join([token.text for token in my_analyzer(alias)])
            if mention in mention2uri:
                mention2uri[mention].append(uri)
            else:
                mention2uri[mention] = [uri]
        pickle.dump(mention2uri, open(output_cleaned_mention2uri_file, 'wb'))
        print(len(mention2uri))

    schema = Schema(title=TEXT(stored=True, analyzer=StemmingAnalyzer()), content=TEXT(stored=True))

    # 创建索引对象
    if not os.path.exists(output_DBindex_dir):
        os.mkdir(output_DBindex_dir)
    ix = create_in(output_DBindex_dir, schema)

    # 添加文档到索引中
    writer = ix.writer()
    for mention, uri in tqdm(mention2uri.items()):
        writer.add_document(title=mention, content=" ".join(uri))
    writer.commit()