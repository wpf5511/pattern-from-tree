import spacy
import sys
import pickle

def createStringRepresent(node):
    res_string = [] 

    current_node_string = node.lemma_+'|'+node.tag_+'|'+node.dep_+'|'+str(node.i)

    res_string.append('(')

    res_string.append(current_node_string)

    children_list = node.children

    children_list = sorted(children_list,key=lambda d:d.lemma_)

    for child in children_list:
        res_string = res_string + createStringRepresent(child)

    res_string.append(')')

    return res_string
        

def bagofwordsRepresent(sent):
    
    l = [token.lemma_ for token in sent] 

    return set(l)






if __name__ =='__main__':

    in_file = sys.argv[1]
    
    out_file = sys.argv[2]

    en_nlp = spacy.load('en')

    lists_of_pattern = []

    with open(in_file,'r') as f_in:
        with open(out_file,'w') as f_out:
            i = 0
            for paragraph in f_in:
                
                paragraph = paragraph.strip()
                if len(paragraph)==0:
                    continue
                
                parsed_par = en_nlp(paragraph)

                for sent in parsed_par.sents:
                    
                    sent_id = i
                    
                    sr = sent.root

                    aa = createStringRepresent(sr)

                    bw = bagofwordsRepresent(sent)
                    
                    #print('\t'.join([str(sent_id),str(aa),str(bw)]),file=f_out)

                    lists_of_pattern.append(aa)

                    i+=1
    
    pattern_binary = open('pattern_binary','w')

    pickle.dump(lists_of_pattern,pattern_binary)

    pattern_binary.close()
    #en_doc = en_nlp('X find a solution to Y')

    #sent = list(en_doc.sents)[0]

    #sr = sent.root

    #aa = createStringRepresent(sr)

    #print(','.join(aa))
    #print(','.join(bagofwordsRepresent(sent)))
