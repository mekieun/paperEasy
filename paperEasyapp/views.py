import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
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
    print('엄마야' + userTextInput)
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
    return render(request, 'third.html', {'link_toReader': readerLink})


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
    return render(request, 'add_comment.html', {'pk':pk})


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
