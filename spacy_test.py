import spacy
import pickle











if __name__ == '__main__':
    en_nlp = spacy.load('en')

    with open('mil_xaa','r') as raw_file:
        texts = raw_file.readlines()
    
    texts = list(map(lambda line:line.strip('\n'),texts))         

    docs_bytes = []

    for doc in en_nlp.pipe(texts,batch_size=10000,n_threads=3):
        doc_bin = doc.to_bytes()
        docs_bytes.append(doc_bin)


    with open('mil_patt','wb') as f_out:
        pickle.dump(docs_bytes,f_out)
