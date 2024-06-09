from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Question, Answer, Comment
from django.db.models import Q
import datetime


def index(request):
    """
    pybo 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어

    # 조회
    question_list = Question.objects.order_by('-create_date')

    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(answer__content__icontains=kw) |  # 답변 내용 검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()
    
    # 페이징처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'pybo/question_list.html', context)


def detail(request, question_id):
    """
    pybo 내용 출력
    """

    print("=====detail=====")
    question = get_object_or_404(Question, pk=question_id)    

    cookie_name = "visited"
    if request.user != None:
        cookie_name = f'visited:{request.user.id}'
    print(cookie_name)

    tomorrow = datetime.datetime.replace(datetime.datetime.now(), hour=23, minute=59, second=0)
    expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    
    if cookie_name in request.COOKIES:  # 쿠키가 있는 경우
        cookie_content = request.COOKIES.get(cookie_name)
        cookies_list = cookie_content.split('|')
        print(cookies_list)

        if str(question_id) not in cookies_list:    # 처음 조회하는 게시물
            print("new")
            question.views += 1
            question.save()

            context = {'question': question}
            response = render(request, 'pybo/question_detail.html', context)
            response.set_cookie(cookie_name, cookie_content + f'|{question_id}')
            
            return response
        else:
            print("old")
            pass
    else:   # 쿠키가 없는 경우
        question.views += 1
        question.save()

        context = {'question': question}
        response = render(request, 'pybo/question_detail.html', context)
        response.set_cookie(cookie_name, question_id, expires=expires)
        
        return response

    context = {'question': question}
    response = render(request, 'pybo/question_detail.html', context)
        
    return response

@login_required(login_url='common:login')
def mypage(request):
    # 입력 파라미터
    question_page = request.GET.get('question_page', '1')       # 질문 페이지
    answer_page = request.GET.get('answer_page', '1')           # 답변 페이지
    comment_page = request.GET.get('comment_page', '1')         # 댓글 페이지

    # 조회
    question_list = Question.objects.filter(author = request.user).order_by('-create_date')
    answer_list = Answer.objects.filter(author = request.user).order_by('-create_date')
    comment_list = Comment.objects.filter(author = request.user).order_by('-create_date')

    # 페이징처리
    question_paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_question_obj = question_paginator.get_page(question_page)

    answer_paginator = Paginator(answer_list, 10)  # 페이지당 10개씩 보여주기
    page_answer_obj = answer_paginator.get_page(answer_page)

    comment_paginator = Paginator(comment_list, 10)  # 페이지당 10개씩 보여주기
    page_comment_obj = comment_paginator.get_page(comment_page)

    context = {
        'question_list': page_question_obj, 
        'answer_list': page_answer_obj,
        'comment_list' : page_comment_obj
    }
    return render(request, 'pybo/mypage.html', context)
