
** chose this option
(gensim + word2vec like model)
https://radimrehurek.com/gensim/models/keyedvectors.html#what-can-i-do-with-word-vectors

https://tedboy.github.io/nlps/generated/generated/gensim.models.Word2Vec.wmdistance.html?highlight=obama


(attempt to run one of many pytorch models)
https://anaconda.org/conda-forge/pytorch-pretrained-bert
conda install -c conda-forge pytorch-pretrained-bert 

(attempt to run pre-trained fastest)
https://anaconda.org/conda-forge/fasttext
conda install -c conda-forge fasttext 
https://fasttext.cc/docs/en/english-vectors.html

(attempt to run BERT as dockerized service)
https://hub.docker.com/r/hazznain/bert-as-service  (nvidia)
docker pull hazznain/bert-as-service

https://hub.docker.com/r/hansonroboticsdev/bert-as-service-cpu
docker pull hansonroboticsdev/bert-as-service-cpu   (cpu)

https://github.com/hanxiao/bert-as-service
pip install bert-serving-client
---
export NUM_WORKER=2
export PATH_MODEL=`pwd`/model_bert
docker run --rm -dit -p 5555:5555 -p 5556:5556 -v $PATH_MODEL:/model hansonroboticsdev/bert-as-service-cpu  $NUM_WORKER
docker run --rm  -p 5555:5555 -it --entrypoint /bin/bash  -p 5556:5556 -v $PATH_MODEL:/model hansonroboticsdev/bert-as-service-cpu

from bert_serving.client import BertClient
bc = BertClient()
bc.encode(['First do it', 'then do it right', 'then do it better'])

