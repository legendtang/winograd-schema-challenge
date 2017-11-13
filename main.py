#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import spacy
import collections
import os
import sys
import xml.etree.cElementTree as ET
from spacy.symbols import *

nlp = spacy.load('en')

# doc1 = nlp(u'Text I do want parsed.')

# doc = nlp(u'London is a big city in the United Kingdom.')
# print(doc[0].text, doc[0].ent_iob, doc[0].ent_type_)
# # (u'London', 2, u'GPE')
# print(doc[1].text, doc[1].ent_iob, doc[1].ent_type_)
# # (u'is', 3, u'')

# tree = ET.ElementTree(file='./WSCollection.xml')
tree = ET.ElementTree(file='./PDPChallenge.xml')
root = tree.getroot()


def resolve_index_to_answer(idx):
    if idx == 0:
        return "A"
    elif idx == 1:
        return "B"
    elif idx == 2:
        return "C"
    else:
        return "D"

def print_statistic():
    # simple statistic
    print "Choices:", choices
    print "Correct Answers:", correct_answer_list
    print "Your Answers:", answer_list

    # calculate rates
    correct_count = 0
    wrong_count = 0
    res_ans = [None] * len(root)
    for i, v in enumerate(correct_answer_list):
        if v == answer_list[i]:
            correct_count += 1
            res_ans[i] = i
        elif v is not None and answer_list[i] is not None:
            wrong_count += 1
            res_ans[i] = -i

    print "Wrong Answer List:", res_ans
    print "Correct Rate:", str(100 * correct_count / len(root)) + "%"
    print "Wrong Rate:", str(100 * wrong_count / len(root)) + "%"



answer_list = [None] * len(root)

# collect choices and correct answers
choices = []
correct_answer_list = []
for child_of_root in root:
    for grandchild_of_root in child_of_root:
        if grandchild_of_root.tag == "answers":
            choices.append([
                grandgrandchild_of_root.text.strip() for grandgrandchild_of_root in grandchild_of_root
            ])
        elif grandchild_of_root.tag == "correctAnswer":
            correct_answer_list.append(grandchild_of_root.text.strip())


count_temp = 0

# process sentence
for cur, child_of_root in enumerate(root):
    text1 = ""
    target = ""
    text2 = ""
    index = -1
    sentence = ""
    quote = ""
    quote_pos = "prepend"
    for grandchild_of_root in child_of_root:
        # extract sentence
        if grandchild_of_root.tag == "text":
            for grandgrandchild_of_root in grandchild_of_root:
                # print grandgrandchild_of_root.tag, grandgrandchild_of_root.text
                if grandgrandchild_of_root.tag == "txt1":
                    text1 = grandgrandchild_of_root.text.replace('  ', ' ')
                elif grandgrandchild_of_root.tag == "pron":
                    target = grandgrandchild_of_root.text
                elif grandgrandchild_of_root.tag == "txt2":
                    text2 = grandgrandchild_of_root.text.replace('  ', ' ')

                if grandgrandchild_of_root == grandchild_of_root[-1]:
                    sentence = (text1 + target + text2).strip().replace('\n',
                                                                        '').replace('\r', '').replace('  ', ' ')
                    target = target.strip()
                    index = len(text1.split())
                    # print(index)

        # extract snippets
        if grandchild_of_root.tag == "quote":
            for grandgrandchild_of_root in grandchild_of_root:
                # print grandgrandchild_of_root.tag, grandgrandchild_of_root.text
                if grandgrandchild_of_root.text is not None:
                    if grandgrandchild_of_root.tag == "quote1":
                        quote += grandgrandchild_of_root.text.replace(
                            '  ', ' ')
                        quote_pos = "prepend"
                    elif grandgrandchild_of_root.tag == "quote2":
                        quote += grandgrandchild_of_root.text.replace(
                            '  ', ' ')
                        quote_pos = "append"
                    else:
                        quote += grandgrandchild_of_root.text.strip()

            # shitty materials!!!!
            quote = quote.strip().replace('.', '').replace('  ', ' ')

        # process text
        if grandchild_of_root == child_of_root[-1]:
            print(sentence)
            document = nlp(sentence.decode('utf8'))
            sentence_list = list(document.sents)

            # try to detect in which sentence
            which_sentence = 0
            # for

            verbs_pre = []
            prps_pre = []
            verbs_post = []
            prps_post = {}
            trunk = collections.OrderedDict()
            pns = []
            adjpns = {}  # second num refers to pos in pns
            despns = {}

            print(quote)
            # quote_list = quote.split()
            # pos = quote_list.index(target)

            # words = sentence.split()
            word_index = -1
            # for i, word in enumerate(words):
            #     if target == word:
            #         if i + 1 <= len(words) - 1 and pos + 1 <= len(quote_list) - 1:
            #             if words[i + 1] == quote_list[pos + 1]:
            #                 word_index = i
            #         if words[i - 1] == quote_list[pos - 1]:
            #             word_index = i
            #         print word_index, word
            # print [(token.text,token.pos_) for token in document]
            for token in document:
                if token.text == target:
                    quote_doc = nlp(quote.decode('utf8'))
                    for quote_tk in quote_doc:
                        if (quote_tk.text == target and
                                (quote_doc[quote_tk.i - 1].text == document[token.i - 1].text or
                                 (quote_tk.i + 1 < len(quote_doc) and token.i + 1 < len(document)
                                  and quote_doc[quote_tk.i + 1].text == document[token.i + 1].text)
                                 )
                            ):
                            if quote_tk.i + 2 < len(quote_doc) and token.i + 2 < len(document):
                                if quote_doc[quote_tk.i + 2].text == document[token.i + 2].text:
                                    word_index = token.i
                                    print token.i, target
                                    count_temp = count_temp + 1
                            else:
                                word_index = token.i
                                print token.i, target
                                count_temp = count_temp + 1

            # print(sentence.find(quote) + quote.find(target))

            # extract specific pos tagging and des and
            # constructtrunk and additional properties
            for possible_subject in document:
                if possible_subject.head.pos == VERB:
                    if not trunk.has_key(possible_subject.head):
                        trunk[possible_subject.head] = [None, None]
                    if possible_subject.dep == nsubj:
                        trunk[possible_subject.head][0] = {
                            possible_subject: possible_subject.i}
                        for possible_pn in possible_subject.children:
                            if possible_pn.dep == poss and possible_pn.pos == ADJ:
                                # print possible_pn.text, possible_subject.text
                                adjpns[possible_pn.text] = possible_subject.text
                            elif possible_pn.dep == appos and possible_pn.pos == PROPN:
                                # print possible_pn.text, possible_subject.text
                                despns[possible_pn.text] = possible_subject.text
                    elif possible_subject.dep == dobj and (possible_subject.pos == PRON or possible_subject.pos == NOUN):
                        trunk[possible_subject.head][1] = {
                            possible_subject: possible_subject.i}
                if possible_subject.head.pos == NOUN and possible_subject.dep == poss:
                    if possible_subject.pos == ADJ:
                        adjpns[possible_subject] = possible_subject.head

            print trunk
            print adjpns
            print despns

            for i, (verb, pn) in enumerate(trunk.iteritems()):
                if pn[0] is not None and word_index in pn[0].itervalues():
                    """ Pronouns as subjects """
                    for num in reversed(xrange(i)):
                        if trunk.items()[num] is not None:
                            for j, ans in enumerate(choices[cur]):
                                # print j, trunk.items()[num][1][0], ans, 88888888888888
                                if trunk.items()[num][1][0] is not None:
                                    for key in trunk.items()[num][1][0].iterkeys():
                                        if not ans.find(key.text):
                                            answer_list[cur] = resolve_index_to_answer(
                                                j)
                                        elif len(choices[cur]) == 2:
                                            print 4444444444444444
                                            answer_list[cur] = resolve_index_to_answer(
                                                1 - j)

                elif pn[1] is not None and word_index in pn[1].itervalues():
                    """ Pronouns as objects """
                    last_idx = -1
                    for num in reversed(xrange(i)):
                        if trunk.items()[num] is not None:
                            if last_idx < 0:
                                last_idx = num
                            for j, ans in enumerate(choices[cur]):
                                # print j, trunk.items()[num][1][0], ans, 88888888888888
                                if trunk.items()[num][1][1] is not None:
                                    for key in trunk.items()[num][1][1].iterkeys():
                                        if not ans.find(key.text):
                                            print len(choices[cur])
                                            answer_list[cur] = resolve_index_to_answer(
                                                j)
                                            continue
                                        elif len(choices[cur]) == 2:
                                            print 4444444444444444
                                            continue
                                            # Don't add that num otherwise more FP
                                            # answer_list[cur] = resolve_index_to_answer(1 - j)
                        if trunk.items()[0][1][1] is None:
                            for j, ans in enumerate(choices[cur]):
                                print trunk.items()[last_idx][1][0]
                                for key in trunk.items()[last_idx][1][0].iterkeys():
                                    if ans.find(key.text):
                                        answer_list[cur] = resolve_index_to_answer(
                                                    j)

            if choices[cur] == None:
                for adj in adjpns:
                    print adj

                    # elif
                    # if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
                    #     verbs_pre.append(possible_subject.head)
                    #     prps_pre.append(possible_subject)
                    #     for possible_pn in possible_subject.children:
                    #         if possible_pn.dep == poss and possible_pn.pos == ADJ:
                    #             print possible_pn.text, possible_subject.i
                    #             adjpns[possible_pn.text] = possible_subject.i
                    #         elif possible_pn.dep == appos and possible_pn.pos == PROPN:
                    #             print possible_pn.text, possible_subject.i
                    #             despns[possible_pn.text] = possible_subject.i
                    #     print possible_subject.i, possible_subject.text
                    # elif possible_subject.dep == dobj and possible_subject.head.pos == VERB:
                    #     verbs_post.append(possible_subject.head)
                    #     prps_post.append(possible_subject)
                    # print(verbs_pre)
                    # print(prps_pre)
                    # print(verbs_post)
                    # print(prps_post)

    # if child_of_root == root[-1]:
    if cur == 4:
        print_statistic()
        exit(0)

