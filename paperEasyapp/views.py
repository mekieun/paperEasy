import re
from datetime import datetime
import matplotlib
import requests
from bs4 import BeautifulSoup
from flask import Flask
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import csv
import pandas as pd
import pandas

import bs4
import requests
import spacy
from spacy import displacy
import en_core_web_sm

nlp = en_core_web_sm.load()
from spacy.matcher import Matcher
from spacy.tokens import Span
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

pd.set_option('display.max_colwidth', 200)
from matplotlib import pyplot as plt_final

# %matplotlib inline


nltk.download('punkt')

app = Flask(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Comment

global reader
reader = ''
global e_link
e_link = 'a'


def home(request):
    return render(request, 'home.html', {})


def second(request):
    global userTextInput
    global totalLen
    global zipped_list

    request.encoding = 'utf-8'
    userTextInput = request.GET['userTextInput']
    linktogo(userTextInput)
    totalLen = len(titles)
    zipped_list = zip(pubid, titles, au_infos_final)
    return render(request, 'second.html',
                  {'userTextInput': userTextInput, 'totalLen': totalLen, 'zipped_list': zipped_list})


def linktogo(lala):
    crawlinglink = requests.get('https://www.ncbi.nlm.nih.gov/pmc/?term=' + lala)  # n-s
    raw = crawlinglink.text
    html = BeautifulSoup(raw, 'html.parser')

    global titles  # 제목
    titles_o = html.select('div.title a')
    titles = []
    for title in titles_o:
        title = remove_tag(str(title))
        titles.append(title)

    global pubid  # 논문id
    pub_id = html.select('dl.rprtid dd')
    pubid = []
    for pub in pub_id:
        pub = remove_tag(str(pub))
        pubid.append(pub)

    global au_infos_final  # 작가
    a_infos = html.select('div.supp')
    au_infos = []
    for i in a_infos:
        au_infos.append(remove_tag(str(i)))
    au_infos_final = []
    for i in range(0, len(au_infos)):
        au_infos_final.append((au_infos[i].split(','))[0:-1])
        au_infos_final[i] = au_infos_final[i][0:int(len(au_infos_final[i]) * 0.05) + 1]


def remove_tag(content):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext


def third(request):
    data = request.GET['theid']
    readerLink = 'https://www.ncbi.nlm.nih.gov/pmc/articles/' + str(data) + '/?report=reader'
    creating_CSV(data)
    csv_to_graph(id_num=str(data[3:]), want_to_search='cells')
    image_path = "static/image_file_" + str(data[3:]) + ".png"
    # 요부분은 html에서 입력받아서 고칠 수 있도록 하기
    return render(request, 'third.html', {'link_toReader': readerLink, 'pmcID': data, 'image_path': image_path})


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'


def add(request):
    data = request.GET['theid']
    crawlinglink = requests.get('https://www.ncbi.nlm.nih.gov/pmc/?term=' + data)
    raw = crawlinglink.text
    html = BeautifulSoup(raw, 'html.parser')
    thetitle = html.select('div.title a')
    title = remove_tag(str(thetitle))
    return render(request, 'add_post.html', {'base_id': data, 'base_title': title})


def create(request):
    if request.method == 'POST':
        post = Post()
        post.title = request.POST['title']
        post.body = request.POST['body']
        post.author = request.user
        post.base_id = request.POST['base_id']
        post.base_title = request.POST['base_title']
        post.publish = datetime.now()
        post.save()
        return redirect('post_detail', str(post.pk))


def createcomment(request, pk):
    if request.method == 'POST':
        comment = Comment()
        comment.post = get_object_or_404(Post, pk=pk)
        comment.body = request.POST['body']
        comment.name = request.user
        comment.date_added = datetime.now()
        comment.save()
        return redirect('post_detail', str(pk))
    return render(request, 'add_comment.html', {'pk': pk})


def update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.title = request.POST['title']
        post.body = request.POST['body']
        post.author = request.user
        post.base_id = request.POST['base_id']
        post.base_title = request.POST['base_title']
        post.publish = datetime.now()
        post.save()
        return redirect('post_detail', str(post.pk))
    return render(request, 'update_post.html', {'post': post})


def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        Post.objects.filter(id=pk).delete()
        return redirect('post_list')
    return render(request, 'delete_post.html', {'post': post})


def find(request):
    data = request.GET['theid']
    posts = Post.objects.all().filter(base_id=data)
    return render(request, 'find_post.html', {'posts': posts})


def remove_tag(content):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext


def remove_css(content):
    cleanr = re.compile('{.*}')
    cleantext = re.sub(cleanr, '', content)
    cleanr = re.compile('\n|\t')
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext


def only_main(content):
    start = content.find('Abstract')
    cleantext = content[start:]
    final = cleantext.find('Article information[\S]+')
    # print('information',final)
    cleantext = cleantext[:final]
    final = cleantext.find('References')
    # print('reference는',final)
    cleantext = cleantext[:final]
    return cleantext


def creating_CSV(num):
    headers = {'User-Agent': 'yumi'}
    url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/'+str(num)+'/'
    req = requests.get(url, headers=headers)

    raw = req.text

    html = BeautifulSoup(raw, 'html.parser')

    e_pubreader_html = html.get_text()
    final_full_text = only_main(remove_css(remove_tag(e_pubreader_html)))
    id = int(num[3:])  # PMC 아이디 값 넣기
    sentList = sent_tokenize(final_full_text)

    f = open('write{}.csv'.format(id), 'w', -1, 'utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(['sentence'])
    for i in sentList:
        wr.writerow([i])

    f.close()


def get_entities(sent):
    ## chunk 1
    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""  # dependency tag of previous token in the sentence
    prv_tok_text = ""  # previous token in the sentence

    prefix = ""
    modifier = ""

    #############################################################

    for tok in nlp(sent):
        ## chunk 2
        # if token is a punctuation mark then move on to the next token
        if tok.dep_ != "punct":
            # check: token is a compound word or not
            if tok.dep_ == "compound":
                prefix = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            # check: token is a modifier or not
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            ## chunk 3
            if tok.dep_.find("subj") == True:
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""

                ## chunk 4
            if tok.dep_.find("obj") == True:
                ent2 = modifier + " " + prefix + " " + tok.text

            ## chunk 5
            # update variables
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
    #############################################################

    return [ent1.strip(), ent2.strip()]


def get_relation(sent):
    doc = nlp(sent)

    # Matcher class object
    matcher = Matcher(nlp.vocab)

    # define the pattern
    pattern = [{'DEP': 'ROOT'},
               {'DEP': 'prep', 'OP': "?"},
               {'DEP': 'agent', 'OP': "?"},
               {'POS': 'ADJ', 'OP': "?"}]

    matcher.add("matching_1", None, pattern)

    matches = matcher(doc)
    k = len(matches) - 1

    span = doc[matches[k][1]:matches[k][2]]

    return (span.text)


def csv_to_graph(id_num, want_to_search):
    candidate_sentences = pd.read_csv("write{}.csv".format(id_num))
    # 여기도 id 값받아서 넣기
    candidate_sentences.shape
    # want_to_search='third 에서 유저인풋 받아서 여기 넣기'
    entity_pairs = []

    for i in tqdm(candidate_sentences['sentence']):
        entity_pairs.append(get_entities(i))

    relations = [get_relation(i) for i in tqdm(candidate_sentences['sentence'])]
    pd.Series(relations).value_counts()[:50]

    # extract subject
    source = [i[0] for i in entity_pairs]

    # extract object
    target = [i[1] for i in entity_pairs]

    kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})

    # create a directed-graph from a dataframe
    G = nx.from_pandas_edgelist(kg_df, "source", "target",
                                edge_attr=True, create_using=nx.MultiDiGraph())

    G = nx.from_pandas_edgelist(kg_df[kg_df['source'] == want_to_search], "edge", "target",
                                edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
    nx.draw(G, with_labels=True, node_color='orange', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)

    # plt.show()

    plt_final.savefig("static/image_file_{}".format(id_num))
