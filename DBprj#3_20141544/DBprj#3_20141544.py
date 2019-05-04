#-*- coding: utf-8 -*-

import datetime
import time
import sys
import MeCab
import operator
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations

DBname = "db20141544"
conn = MongoClient('dbpurple.sogang.ac.kr')
db = conn[DBname]
db.authenticate(DBname,DBname)
stop_word = {}
cnt = 0
def printMenu():
    print "0. CopyData"
    print "1. Morph"
    print "2. print morphs"
    print "3. print wordset"
    print "4. frequent item set"
    print "5. association rule"

def p0():
    col1 = db['news']
    col2 = db['news_freq']

    col2.drop()

    for doc in col1.find():
        contentDic = {}
        for key in doc.keys():
            if key != "_id":
                contentDic[key] = doc[key]
        col2.insert(contentDic)
def p1():
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update( {"_id":doc['_id']},doc)
def p2(url):
    for doc in db['news_freq'].find({'url' : url}):
        for w in doc['morph']:
            print(w.encode('utf-8'))
    
def p3():
    col1 = db['news_freq']
    col2 = db['news_wordset']
    col2.drop()
    for doc in col1.find():
        new_doc = {}
        new_set = set()
        for w in doc['morph']:
            new_set.add(w.encode('utf-8'))
        new_doc['word_set'] = list(new_set)
        new_doc['url'] = doc['url']
        col2.insert(new_doc)
def p4(url):
    for doc in db['news_wordset'].find({'url' : url}):
        for w in doc['word_set']:
            print(w.encode('utf-8'))
def p5(length):
    candidate_name = "candidate_L"+(str)(1)
    col1 = db[candidate_name]
    col2 = db['news_wordset']
    col1.drop()
    wordlist = []
    comb = []
    count = 0 
    dic = {}
    num = col2.find().count()
    for wordset in col2.find():
        for word in wordset['word_set']:
            if word not in dic:
                dic[word] = 1
            else:
                dic[word] += 1
    for word in dic: 
        if dic[word]>=num*0.1:
            new_doc = {}
            wordlist.append(word) #1개짜리 list 만듬
            new_doc['item_set'] = word
            new_doc['support'] = dic[word]
            col1.insert(new_doc)
    for i in range(0,length-1):
        candidate_name = "candidate_L"+(str)(i+2)
        col1 = db[candidate_name]
        col1.drop()
        dic2 = {}
        comb = combinations(wordlist,2)
        wordlist = list(comb)
        for wordset in col2.find():
            dic3 = {}
            for subset in wordlist:
                c = set(subset)
                if i!=0 :
                    set1 = set()
                    for a in c:
                        set1 = set1.union(a)
                    c = frozenset(set1)
                    if c not in dic3:
                        dic3[c] = 1
                    else:
                        count+=1
                        continue
                    if len(c)!= i+2:
                        continue
                if c.issubset(wordset['word_set']):
                   f = frozenset(c)   
                   if f not in dic2:
                       dic2[f] = 1
                   else:
                       dic2[f] += 1
        wordlist = set()
        for word in dic2:
            if dic2[word] >= num*0.1:
                new_doc = {}
                wordlist.add(frozenset(word))
                new_doc['item_set'] = list(word)
                new_doc['support'] = dic2[word]
                col1.insert(new_doc)

#print(count)
def p6(length):
    L1 = db['candidate_L1']
    L2 = db['candidate_L2']
    L3 = db['candidate_L3']
    string = 'candidate_L' + str(length)
    result1 = 0
    result2 = 0
    result3 = 0
    for doc in db[string].find():
        temp = doc['item_set']
        a = temp[0]
        b = temp[1]
        count = 0
        if length == 3:
            c = temp[2]
        total_freq = doc['support']
        for doc in L1.find():
            small_freq = doc['support']
            if doc['item_set'] == a:
                result1 = cal(total_freq,small_freq)
                count = 1
            if doc['item_set'] == b:
                result2 = cal(total_freq,small_freq)
                count = 2
            if length == 3:
                if doc['item_set'] == c:
                    result3 = cal(total_freq,small_freq)
                    count = 3
        if result1/100 >= 0.5:
            sys.stdout.write(a + ' =>' + b)
            if length == 3:
                sys.stdout.write(' ,' + c)
            sys.stdout.write('  ')
            sys.stdout.write( str(cal1(result1)))
            print(' ')
        if result2/100 >= 0.5:
            sys.stdout.write(b + ' =>' + a)
            if length == 3:
                sys.stdout.write(' ,' + c)
            sys.stdout.write('  ')
            sys.stdout.write(str(cal1(result2)))
            print(' ')
        if result3/100 >= 0.5:
            sys.stdout.write(c + ' =>' + a + ' ,' + b + '    ')
            sys.stdout.write(str(cal1(result3)))
            print(' ')
        result1 =0
        result2 = 0
        result3 = 0
                
    if length == 3:
        result1 =0
        result2 =0
        result3 =0
        for doc in db[string].find():
            temp = doc['item_set']
            total_freq = doc['support']
            comb = list(combinations(temp,2))
            e1 = [temp[0],temp[1]]
            e2 = [temp[1],temp[2]]
            e3 = [temp[0],temp[2]]
            e4 = comb[0]
            e5 = comb[1]
            e6 = comb[2]
            if e1 == e4:
                cnt +=1
            if e2 == e5:
                cnt +=1
            if e3 == e6:
                cnt +=1
            #print(cnt)
            for doc in L2.find():
                small_freq = doc['support']
                if set(e1).issubset(doc['item_set']): 
                    result1 = cal(total_freq,small_freq)
                if set(e2).issubset(doc['item_set']):
                   result2 = cal(total_freq,small_freq)
                if set(e3).issubset(doc['item_set']):
                   result3 = cal(total_freq,small_freq)

            if result1/100 >= 0.5:
                sys.stdout.write(temp[0] + ' ,' + temp[1] + ' =>' + temp[2] + '    ')
                sys.stdout.write(str(cal1(result1)))
                print(' ')
            if result2/100 >= 0.5:
                sys.stdout.write(temp[1] + ' ,' + temp[2] + ' =>' + temp[0] + '    ')
                sys.stdout.write(str(cal1(result2)))
                print(' ')
            if result3/100 >= 0.5:
                sys.stdout.write(temp[0] + ' ,' + temp[2] + ' =>' + temp[1] + '    ')
                sys.stdout.write(str(cal1(result3)))
                print(' ')
def cal(a,b):
    c = float(a)/b
    c*= 100.0
    return c
def cal1(a):
    return a/100
def make_stop_word():
    f = open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()
def morphing(content):
    t = MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    nodes = t.parseToNode(content.encode('utf-8'))
    MorpList = []
    while nodes:
        if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
            w = nodes.surface
            if not w in stop_word:
                try:
                    w = w.encode('utf-8')
                    MorpList.append(w)
                except:
                    pass
        nodes = nodes.next
    return MorpList

if __name__ == "__main__":
    make_stop_word()
    printMenu()
    selector = input()
    if selector == 0:
        p0()
    elif selector == 1:
        p1()
        p3()
    elif selector == 2:
        url = str(raw_input("input news url:"))
        p2(url)
    elif selector == 3:
        url = str(raw_input("input news url:"))
        p4(url)
    elif selector == 4:
        length = int(raw_input("input length of the frequent item:"))
        p5(length)
    elif selector == 5:
        length = int(raw_input("input length of the frequent item:"))
        p6(length)
    

