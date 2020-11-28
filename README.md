# PivotsCR
We released the used QALD data and code for the paper entitled "Pivots-based Candidate Retrieval for Cross-lingual Entity Linking"
# QALD Data
The original QALD 4-9 dataset is available [here](https://github.com/ag-sc/QALD).  

The used **Knowledge Base** is  DBpedia 2016-10. Please download the KB from this [link](https://wiki.dbpedia.org/downloads-2016-10).

We processed this dataset for cross-lingual entity linking task, and result files are in **QALD_data** folder:
  - **QALD_multilingual4-9.json**: we merged multilingual QALD 4-9 data, and then extracted examples which can be execute on DBpedia 2016-10. This file can be used for cross-lingual entity linking and cross-lingual question answering over knowledge base. 
  - **QALD_XEL folder**. We extracted data for cross-lingual entity linking spanning eight languages. Below is an example: 
 ```ruby
    {
        "context": "Gib mir alle Filme mit Tom Cruise.",
        "id": 13,
        "keywords": [
            "Film",
            "Tom Cruise"
        ],
        "uris": [
            "<http://dbpedia.org/ontology/Film>",
            "<http://dbpedia.org/resource/Tom_Cruise>"
        ]
    },
```

## Code
**Step1:** Preparing cross-lingual entity linking data and the corresponding Knowledge Base.
 
 **Step2:** Generating aligned word embedding for source language (e.g., German) and target language (English) by
 - Directly download the published aligned word vectors for 44 languages based on the pre-trained vectors computed on Wikipedia using fastText for [here](https://fasttext.cc/docs/en/aligned-vectors.html). Or
 - Employ [MUSE](https://github.com/facebookresearch/MUSE) to align monolingual word embeddings:
	 - **supervised**: using a train bilingual dictionary to learn a mapping from the source to the target space.
	- **unsupervised**: without any parallel data or anchor point, learn a mapping from the source to the target space using adversarial training and (iterative) Procrustes refinement.

**Step3:** Generate Plausible English Mentions

 - Search the most similar English words for each word in a source-language mention. In this paper, we used the CSLS (Cross-domain similarity local scaling) proposed by [MUSE](https://github.com/facebookresearch/MUSE). Alternatively, you can also employ the cosine similarity of vectors to measure the word similarity and [GENSIM](https://radimrehurek.com/gensim/models/keyedvectors.html) is suggested.
 - Clean the similar words using NMS algorithm, and generated plausible English mentions for each source mention
	 ```
	 python SemanticNMS.py
	 ```
 
**Step4:**  Lexical Retrieval and Generate TopN Candidates
 - Generate all entities in KB. In our paper, we used the DBpedia 2016-10, which contains ~6million entites. E.g.,
	 ``` 
	bash download.sh		# download the KB
	python Gen_KB_entities.py 	# generate all entities in KB
	 ```
 - Build search index for all entities.  In this paper, we build the Index using [Whoosh](https://whoosh.readthedocs.io/en/latest/index.html), which is a library of classes and functions for indexing text and then searching the index. E.g.,
  	```
	python Build_KB_Index.py
	``` 
 - Search the plausible mentions, return top-1000 candidates. E.g., 
 	```
	python LexicalSearch.py
	``` 
