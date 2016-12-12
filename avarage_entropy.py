import spacy
import numpy as np
from collections import Counter

def getEntropy(slot_lists):
    c = Counter(slot_lists)
    ss = sum(c.values())
    H = 0
    for k,v in c.items():
        px = v/ss
        H += -px*np.log2(px)
    
    return H


if __name__ == '__main__':
    with open('mil_xaa','r') as f_in:
        texts = f_in.readlines()

        text =''.join(texts)

    en_nlp = spacy.load('en')

    en_doc = en_nlp(text)

    ave = getEntropy(list(en_doc))

    print(ave) 
