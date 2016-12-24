import spacy
import pdb
from zss import Node
import pickle
from collections import Counter
from spacy.tokens.doc import Doc
import copy
import numpy as np

def getEntropy(slot_lists):
    c = Counter(slot_lists)
    ss = sum(c.values())
    H = 0
    for k,v in c.items():
        px = v/ss
        H += -px*np.log2(px)
    
    return H

def getBackPattern(node,pattern,depth):
    if depth==4:
        #nothing
        return
    else:
        curPnode = Node(node.lemma_+'|'+node.tag_+'|'+node.dep_+'|'+str(node.i))
        if not pattern:
            pattern = curPnode
            pattern.nodes =[]
            pattern.nodes.append(curPnode)

        else:
            original_parent = node.head
            parent_label = original_parent.lemma_+'|'+original_parent.tag_+'|'+original_parent.dep_+'|'+str(original_parent.i)
            inserted_Node = pattern.get(parent_label)
            
            inserted_Node.addkid(curPnode)
            pattern.nodes.append(curPnode)
            curPnode.parent = inserted_Node

        if not node.children:
            #nothing
            #LCS(pattern,candicate_sent)
            pass
        else:
            if depth==0:
                pattern_list=[]
                if list(node.children):
                    for child in node.children:
                        valued_pattern = copy.deepcopy(pattern)
                        getBackPattern(child,valued_pattern,depth+1)
                        pattern_list.append(valued_pattern)
                else:
                    pattern_list.append(pattern)
                return pattern_list
            else:
                for child in node.children:
                    getBackPattern(child,pattern,depth+1)

def getBackEntropy(node):
    pat = None
    pat_list = getBackPattern(node,pat,0)

    global spacy_sents
    max_entropy=0
    for bac_pat in pat_list:
        slot_values=[]
        for candicate_sent in spacy_sents:
            matched,match_res = LCS(bac_pat,candicate_sent,True)
            if matched:
                slot_values.extend(match_res)
        if slot_values:
            cur_En = getEntropy(slot_values)
            if cur_En>max_entropy:
                max_entropy = cur_En
    return max_entropy 
    
def dfs(num,match_res,len_p,d,nodes,back):
    if num==len_p:
        if back:
            match_res.append(d.get(nodes[0]).head)
        else:
            match_res.append(d.get(nodes[len_p-1]))
        return 
    pNode = nodes[num]
    
    pNode_parent = pNode.parent

    parent_matched = d[pNode_parent]

    for sent_child in parent_matched.children:
        if unit_equal(pNode.label,sent_child):
            d[pNode] = sent_child
            dfs(num+1,match_res,len_p,d,nodes,back)



def LCS(pattern,candicate_sent,back=False):
    label_proot = pattern.label

    root_match_tokens = [token for token in candicate_sent if unit_equal(label_proot,token) ]

    d={}
    
    len_p = len(pattern.nodes)

    match_res =[]
    
    nodes = pattern.nodes
    
    for rmt in root_match_tokens:
        d[nodes[0]]= rmt
        dfs(1,match_res,len_p,d,nodes,back)
    
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
            
            curpH= getEntropy(slot_values)
            curbpH = getBackEntropy(node)
            print('curpH:{},prevH:{}'.format(curpH,prevH))
            print('curbpH:{}'.format(curbpH))

            if curpH>prevH and curbpH>prevH:
                #this node is argnode 
                newpattern = None

                global spacy_sents

                if list(node.children):
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

            if list(node.children):
                global spacy_sents

                newpattern = None

                getPattern(newpattern,node,spacy_sents,startH)


                



if __name__ == '__main__':
    en_nlp = spacy.load('en')
    
    pattern_list = []

    docs=[]

    with open('/home/wpf/wiki/branch_entropy/mil_patt','rb') as patt_file:
        docs_bytes = pickle.load(patt_file)

    for byte in docs_bytes:
        docs.append(Doc(en_nlp.vocab).from_bytes(byte))
    
    spacy_sents = []
    
    for doc in docs:
        spacy_sents.extend(list(doc.sents))
 
    while True:
        input_text = input("input a sent:\n")
                
        en_doc = en_nlp(input_text)
    
        for sent in en_doc.sents:
            sr = sent.root
            spattern = None
            startH = 4.0 
            getPattern(spattern,sr,spacy_sents,startH)
    
    #assert len(pattern_list)==1 

    #with open('/home/wpf/wiki/branch_entropy/example_pattern','wb') as f_out:
    #    pickle.dump(pattern_list,f_out)

        for p in pattern_list:
            print(p)
            print('------------')
    #print(pattern_list)
