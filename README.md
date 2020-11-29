# PivotsCR
We released the used QALD data and code for the paper entitled "Pivots-based Candidate Retrieval for Cross-lingual Entity Linking".
# QALD Data
The original QALD 4-9 datasets are available [here](https://github.com/ag-sc/QALD).  

We processed these datasets for cross-lingual entity linking task. We merged multilingual QALD 4-9 data. These examples are cross-lingual question answering over different knowledge bases. We extracted examples which can be execute on DBpedia 2016-10. Please download this knowledge base from this [link](https://wiki.dbpedia.org/downloads-2016-10). We provided our code to download this knowledge base and extract its all entities for reference. E.g., 
 ``` ruby
	bash download.sh		# download the KB files
	python Gen_KB_entities.py 	# generate all entities in KB
```

The result files are in **QALD_data** folder:
  - **QALD_multilingual4-9.json**: This file can be used for cross-lingual entity linking and cross-lingual question answering over knowledge base. 
  - **QALD_XEL folder**. We extracted data for cross-lingual entity linking spanning eight languages. Below are sevearl examples: 
 ```ruby
    # an example in QALD_XEL/qald_de.json
    {
        "context": "Wer ist der König der Niederlande?",
        "id": 562,
        "keywords": [
            "König",
            "Niederlande"
        ],
        "uris": [
            "<http://dbpedia.org/ontology/Royalty>",
            "<http://dbpedia.org/resource/Netherlands>"
        ]
    },
    # an example in QALD_XEL/qald_ro.json
    {
        "context": "Dă-mi toate prenumele feminine.",
        "id": 30,
        "keywords": [
            "feminine",
            "prenume"
        ],
        "uris": [
            "<http://dbpedia.org/resource/Female>",
            "<http://dbpedia.org/ontology/GivenName>"
        ]
    }
```

## Code
**Step1:** Preparing cross-lingual entity linking data and the corresponding Knowledge Base.
 
**Step2:** Generating aligned word embedding for source language (e.g., German) and target language (English) by
 - Directly download the published aligned word vectors by fastText from [here](https://fasttext.cc/docs/en/aligned-vectors.html). E.g.,
	  ```ruby
	  # download aligned word embeddings
		 wget https://dl.fbaipublicfiles.com/fasttext/vectors-aligned/wiki.en.align.vec
		 wget https://dl.fbaipublicfiles.com/fasttext/vectors-aligned/wiki.de.align.vec
	```
 - Employ [MUSE](https://github.com/facebookresearch/MUSE) to align monolingual word embeddings:
	- **supervised**: using a bilingual dictionary to learn a mapping from the source to the target space.
	- **unsupervised**: without any parallel data or anchor point, learn a mapping from the source to the target space using adversarial training and (iterative) Procrustes refinement.

**Step3:** Generate Plausible English Mentions

 - Search the most similar English words for each word in a source-language mention. In this paper, we used the CSLS (Cross-domain similarity local scaling) proposed by [MUSE](https://github.com/facebookresearch/MUSE). Alternatively, you can employ the cosine similarity of vectors to measure the word similarity and [GENSIM](https://radimrehurek.com/gensim/models/keyedvectors.html) is suggested. E.g.,
	 ```ruby
	 # generate similar words
	 import gensim
	 en_word_vectors = gensim.models.KeyedVectors.load_word2vec_format("wiki.en.align.vec", binary=False)
	 de_word_vectors = gensim.models.KeyedVectors.load_word2vec_format("wiki.de.align.vec", binary=False)

	 for word in de_mention.split(" "):# de_mention is the string of a German mention, e.g., de_mention = "Vincent van Gogh"
		print(word, en_word_vectors.similar_by_vector(de_word_vectors[word],topn=20))
	 ```

 - Clean the similar words using NMS algorithm, and generate a set of plausible English mentions for each source mention.
	 ```
	 python SemanticNMS.py
	 ```
 
**Step4:**  Lexical Retrieval and Generate TopN Candidates
 - Generate all entities in KB. In our paper, we used the DBpedia 2016-10, which contains ~6million entites. E.g.,
	
 - Build search index for all entities.  In this paper, we build the index of all entities in KB using [Whoosh](https://whoosh.readthedocs.io/en/latest/index.html), which is a library of classes and functions for indexing text and then searching the index. E.g.,
  	```
	python Build_KB_Index.py
	``` 
 - Search the plausible mentions, return top-1000 candidates. E.g., 
 	```
	python LexicalSearch.py
	``` 
