from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from .models import *
from .search import *
# from .search import *
from django.contrib.auth.decorators import login_required
import json
from .userCF import *

stopwords = []
index = {}
titles = {}
categories = {}

# Create your views here.n
def home(request):
    log_status = request.user.is_authenticated()
    Cate = Categories.objects.all()
    Article = Newsinfo.objects.all().order_by('?')[:20]
    return render(request,'home1.html',{'log_status': log_status, 'category': Cate, "articles": Article})

def newssearch(request):
    log_status = request.user.is_authenticated()
    Cate = Categories.objects.all()
    words = request.GET.get('words')
    if not len(stopwords):
        print('222222')
        # jieba.load_userdict('dict.txt')
        # load_stopwords()
        # load_sql()
        # get_all_titles()
        # load_category()
        jieba.load_userdict('dict.txt')
        load_stopwords()
        load_sql()
        get_all_titles()
        load_category()
        print('11111')
    results = search(words)
    Article = []
    for result in results:
        Article.append(Newsinfo.objects.get(article_id=result))
    return render(request, 'home.html', {'log_status': log_status, 'category': Cate, "articles": Article})

def cate(request,Category_name):
    log_status = request.user.is_authenticated()
    Cate = Categories.objects.all()
    Article_count = int(request.GET.get('page', "0"))
    more = True
    if Article_count == 0:
        Article_count = 1
    else:
        Article_count += 1
    Article = Menus.objects.filter(name=Category_name)[:Article_count*10]
    News = []
    for a in Article:
        News.append(Newsinfo.objects.get(article_id=a.article_id))
    if Article.count() != Article_count * 10:
        more = False
    return render(request, 'home.html', {'log_status': log_status, 'category': Cate, "articles": News,
                                         'count': Article_count, 'more': more})

def login(request):
    log_status = request.user.is_authenticated()
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html',
                          {'password_is_wrong': True, 'log_status': log_status})
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    respon = redirect('/')
    return respon

def news_detail(request, Article_id):
    log_status = request.user.is_authenticated()
    if log_status:
        user = Userinfo.objects.get(username=request.user.get_username())
        news = Newsinfo.objects.get(article_id=Article_id)
        tmp = Usercf.objects.filter(username=user, article=news)
        if tmp.count() == 0:
            Usercf.objects.create(username=user, article=news, rate=3.0)
    article = Newsinfo.objects.get(article_id=Article_id)
    id = Menus.objects.filter(article_id=Article_id)[0]
    cat = id.name
    Cate = Categories.objects.all()
    div = "div/" + str(Article_id) + ".txt"
    return render(request, 'news_detail.html', {'log_status': log_status, 'article': article, 'category': Cate,
                                                 'div': div, 'cat': cat})

@login_required(login_url="/login")
def setrate(request):
    user = Userinfo.objects.get(username=request.user.get_username())
    if request.method == 'GET':
        Article_id = request.GET.get('article')
        news = Newsinfo.objects.get(article_id=Article_id)
        Usercf.objects.filter(username=user, article=news).delete()
        Usercf.objects.create(username=user, article=news, rate=5.0)
        return news_detail(request, Article_id)
    elif request.method == 'POST':
        Article_id = request.POST.get('article')
        news = Newsinfo.objects.get(article_id=Article_id)
        Usercf.objects.get(username=user, article=news).update(rate=1.0)
        return news_detail(request, Article_id)

def signin(request):
    log_status = request.user.is_authenticated()
    if request.method == 'GET':
        return render(request, 'signin.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        filterResult = User.objects.filter(username=username)  # c************
        if len(filterResult) == 0:
            User.objects.create_user(username=username, password=password)
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                Userinfo.objects.create(username=username, psw=password)
                auth.login(request, user)
                return redirect('/')
        else:
            return render(request, 'login.html',
                          {'password_is_wrong': True, 'log_status': log_status})
    return render(request, 'signin.html')

def fuzzy(request):
    Key = request.GET['key']
    results = fuzzyfinder(Key)[:5]
    print(results)
    return HttpResponse(json.dumps(results), content_type='application/json')