import spacy
import pdb
from zss import Node
import pickle
from collections import Counter
from spacy.tokens.doc import Doc
import numpy as np

def getEntropy(slot_lists):
    c = Counter(slot_lists)
    ss = sum(c.values())
    H = 0
    for k,v in c.items():
        px = v/ss
        H += -px*np.log2(px)
    
    return H

def dfs(num,match_res,len_p,d,nodes):
    if num==len_p:
        match_res.append(d.get(nodes[len_p-1]))
        return 

    pNode = nodes[num]
    
    pNode_parent = pNode.parent

    parent_matched = d[pNode_parent]

    for sent_child in parent_matched.children:
        if unit_equal(pNode.label,sent_child):
            d[pNode] = sent_child
            dfs(num+1,match_res,len_p,d,nodes)



def LCS(pattern,candicate_sent):
    label_proot = pattern.label

    root_match_tokens = [token for token in candicate_sent if unit_equal(label_proot,token) ]

    d={}
    
    len_p = len(pattern.nodes)

    match_res =[]
    
    nodes = pattern.nodes
    
    for rmt in root_match_tokens:
        d[nodes[0]]= rmt
        dfs(1,match_res,len_p,d,nodes)
    
    if not match_res:
        matched = False
    else:
        #print('have matched')
        matched = True
    
    match_res = map(lambda token:(token.lemma_,token.tag_),match_res)

    return matched,match_res




def unit_equal(plabel,token):
    p_tri = plabel.split('|')
    s_tri = '|'.join([token.lemma_,token.tag_,'*' if token.dep_=='ROOT' else token.dep_,str(token.i)])
    s_tri = s_tri.split('|')

    if len(p_tri)==4 and len(s_tri)==4:
        return all([s1=='*' or s2=='*' or s1==s2 for s1,s2 in zip(p_tri[:-1],s_tri[:-1])])
    else:
        return False



# pattern is a root of a tree Node, node type is token in spacy
def getPattern(pattern,node,candidate_sents,prevH):
    if not candidate_sents:
        pass
    global pattern_list
    global startH

    if not pattern:
        curPnode = Node(node.lemma_+'|'+node.tag_+'|'+('*' if node.dep_=='ROOT' else node.dep_)+'|'+str(node.i))

        pattern = curPnode

        pattern.nodes=[]

        pattern.nodes.append(curPnode)

        pattern_list.append(pattern)

        children_list = node.children

        for child in children_list:
            getPattern(pattern,child,candidate_sents,prevH)
    else:
        dep_str = node.dep_

        pnode_label = '*|*|'+dep_str+'|'+str(node.i)

        original_parent = node.head
        
        parent_label = original_parent.lemma_+'|'+original_parent.tag_+'|'+('*' if original_parent.dep_=='ROOT' else original_parent.dep_)+'|'+str(original_parent.i)

        inserted_Node = pattern.get(parent_label)

        if not inserted_Node:
            parent_label = '*|*|'+('*' if original_parent.dep_=='ROOT' else original_parent.dep_)+'|'+str(original_parent.i)

            inserted_Node = pattern.get(parent_label)

        argnode = Node(pnode_label) 

        try:
            inserted_Node.addkid(argnode)
            pattern.nodes.append(argnode)
            argnode.parent = inserted_Node
        except:
            print('error point')
            print(repr(pattern))
            print(parent_label)

        slot_values = []
        filtered_candicates = []

        for candicate_sent in candidate_sents:
            matched,match_res = LCS(pattern,candicate_sent)
            if matched:
                slot_values.extend(match_res)
                filtered_candicates.append(candicate_sent)

        print('cur node label:{},candicate_len:{}'.format(node.lemma_,len(filtered_candicates)))

        if filtered_candicates:
            
            curpH = getEntropy(slot_values)

            print('curpH:{},prevH:{}'.format(curpH,prevH))

            if curpH>prevH:
                #this node is argnode 
                newpattern = None

                global spacy_sents
                
                getPattern(newpattern,node,spacy_sents,startH)
            
            else:
                #this node should be normal node
                argnode.label = node.lemma_+'|'+node.tag_+'|'+node.dep_+'|'+str(node.i)
                
                children_list = node.children
                
                for child in children_list:
                     getPattern(pattern,child,filtered_candicates,curpH)
        else:
            #corpus doesn't matched pattern 
            inserted_Node.children.pop()
            pattern.nodes.pop()


                



if __name__ == '__main__':
    en_nlp = spacy.load('en')
    
    en_doc = en_nlp('A few accessories such as a pair of sunglasses or silver loops on the wrist can add up to the romance sphere.')

    pattern_list = []

    docs=[]

    with open('/home/wpf/wiki/branch_entropy/mil_patt','rb') as patt_file:
        docs_bytes = pickle.load(patt_file)

    for byte in docs_bytes:
        docs.append(Doc(en_nlp.vocab).from_bytes(byte))
    
    spacy_sents = []
    
    for doc in docs:
        spacy_sents.extend(list(doc.sents))
             
    for sent in en_doc.sents:
        sr = sent.root
        spattern = None
        startH = 4.0 
        getPattern(spattern,sr,spacy_sents,startH)
    
    #assert len(pattern_list)==1 

    with open('/home/wpf/wiki/branch_entropy/example_pattern','wb') as f_out:
        pickle.dump(pattern_list,f_out)

    for p in pattern_list:
        print(p)
        print('------------')
    #print(pattern_list)
