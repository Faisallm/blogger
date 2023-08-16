from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger
from .forms import EmailPostForm


def post_list(request):
    posts = Post.published.all()
    # 3 posts per page
    paginator = Paginator(posts, 3)
    # get the page number from the http get request
    # if the page number does not exist
    # set default as 1
    page_number = request.GET.get('page', 1)
    # get the posts from the request of the required page
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # return the last page
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # if we mistakenly pass a string
        # we return the first page.
        posts = paginator.page(1)

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post,
                             slug=post,
                             status=Post.Status.PUBLISHED,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
