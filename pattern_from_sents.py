import spacy
import pdb
from zss import Node
import pickle
from collections import Counter
import numpy as np

def getEntropy(slot_lists):
    c = Counter(slot_lists)
    ss = sum(c.values())
    H = 0
    for k,v in c.items():
        px = v/ss
        H += -px*np.log2(px)
    
    return H


def isArgnode(nodeStr):
    node_qua = nodeStr.split()
    if len(node_qua)!=4:
        return False
    elif node_qua[:-2]==['*','*']:
        return True
    else:
        return False

def LCS(pattern_string,sent_string):
    
    len_p = len(pattern_string)
    
    len_s = len(sent_string)
    
    c = [[0 for i in range(len_s+1)] for j in range(len_p+1)]

    flag = [[0 for i in range(len_s+1)] for j in range(len_p+1)]

    for i in range(len_p):
        for j in range(len_s):
            if unit_equal(pattern_string[i],sent_string[j]):
                c[i+1][j+1] = c[i][j]+1
                flag[i+1][j+1]='ok'
            elif c[i+1][j]>c[i][j+1]:
                c[i+1][j+1]=c[i+1][j]
                flag[i+1][j+1]='left'
            else:
                c[i+1][j+1]=c[i][j+1]
                flag[i+1][j+1]='up'
    if c[-1][-1]!=len_p:
        matched = False
    else:
        matched = True

    match_res = []

    x = len_p 
    
    #for ease we only use one result
    
    #y_list = [y for y in range(len_s+1) if c[x][y]==len_p]
    
    y = len_s

    while x!=0 and y!=0:
        if flag[x][y]=='ok':
            if isArgnode(pattern_string[x-1]):
                match_res.append(sent_string[y-1])
                break
            x -= 1
            y -= 1
        elif flag[x][y]=='left':
            y -= 1
        else:
            x -= 1
    

    return matched,match_res




def unit_equal(pattern_unit,sent_unit):
    if pattern_unit==sent_unit:
        return True
    else:
        p_tri = pattern_unit.split('|')
        s_tri = sent_unit.split('|')

        if len(p_tri)==4 and len(s_tri)==4:
            return all([s1=='*' or s2=='*' or s1==s2 for s1,s2 in zip(p_tri[:-1],s_tri[:-1])])
        else:
            return False


def createStringforPattern(Tnode):
    res_string = [] 

    current_node_string = Tnode.label

    res_string.append('(')

    res_string.append(current_node_string)

    children_list = Tnode.children

    children_list = sorted(children_list,key=lambda d:(d.label).split('|')[0])

    for child in children_list:
        res_string = res_string + createStringforPattern(child)

    res_string.append(')')

    return res_string


# pattern is a root of a tree Node, node type is token in spacy
def getPattern(pattern,node,candidate_patterns,prevH):
    if not candidate_patterns:
        pass
    global pattern_list
    global startH
    if not pattern:
        pattern = Node(node.lemma_+'|'+node.tag_+'|'+ '*' if node.dep_=='ROOT' else node.dep_+'|'+str(node.i))

        pattern_list.append(pattern)

        children_list = node.children

        children_list = sorted(children_list,key=lambda d:d.lemma_)

        for child in children_list:
            getPattern(pattern,child,candidate_patterns,prevH)
    else:
        dep_str = node.dep_

        pnode_label = '*|*|'+dep_str+'|'+str(node.i)

        original_parent = node.head
        
        parent_label = original_parent.lemma_+'|'+original_parent.tag_+'|'+ '*' if original_parent.dep_=='ROOT' else original_parent.dep_ +'|'+str(original_parent.i)

        inserted_Node = pattern.get(parent_label)

        argnode = Node(pnode_label) 

        try:
            inserted_Node.addkid(argnode)
        except:
            print('error point')
            print(repr(pattern))
            print(parent_label)

        # match the pattern in the sentence
        pattern_string = createStringforPattern(pattern)

        slot_values = []
        filtered_candicate = []

        for sent_string in candidate_patterns:
            matched,match_res = LCS(pattern_string,sent_string)
            if matched:
                slot_values.extend(match_res)
                filtered_candicate.append(sent_string)

        curpH = getEntropy(slot_values)

        if curpH>prevH:
            newpattern = None 
             
            global sents_string
            getPattern(newpattern,node,sents_string,startH)
        else:
             #%replace argnode with normal node%

             argnode.label = node.lemma_+'|'+node.tag_+'|'+node.dep_+'|'+str(node.i)
             
             children_list = node.children

             children_list = sorted(children_list,key=lambda d:d.lemma_)

             for child in children_list:
                 getPattern(pattern,child,candidate_patterns,curpH)



                










if __name__ == '__main__':
    pdb.set_trace()
    en_nlp = spacy.load('en')
    
    en_doc = en_nlp('Anarchism draws on many currents of thought and strategy.')

    pattern_list = []

    with open('/home/wpf/wiki/branch_entropy/sample_sents_patterns','r') as sent_file:
        sents_string = [eval(line) for line in sent_file]
    
    #sents_string = %read from file%

    for sent in en_doc.sents:
        sr = sent.root
        spattern = None
        startH = np.inf
        getPattern(spattern,sr,sents_string,startH)

    with open('/home/wpf/wiki/branch_entropy/example_pattern','wb') as f_out:
        pickle.dump(pattern_list,f_out)

    print(pattern_list)
