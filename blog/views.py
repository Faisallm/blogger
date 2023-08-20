from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, \
    SearchQuery, SearchRank


def post_list(request, tag_slug=None):
    posts = Post.published.all()

    tag = None
    if tag_slug:
        # get the requested tag
        tag = get_object_or_404(Tag, slug=tag_slug)
        # filter posts by tags
        posts = posts.filter(tags__in=[tag])

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
                  {'posts': posts,
                   'tag': tag})


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post,
                             slug=post,
                             status=Post.Status.PUBLISHED,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
        .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


# we use both the same view for displaying the initial form
# and processing the submitted data
def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id,
                             status=Post.Status.PUBLISHED)

    sent = False

    if request.method == "POST":
        # form is submitted
        # fill form with prepopulated data
        form = EmailPostForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            # build the url of the post
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends that you read"\
                f"{post.title}"
            message = f"Read {post.title} at {post_url} \n\n"\
                f"{cd['name']}\s comments: {cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True

            # logic for sending email

    else:
        form = EmailPostForm()

    return render(request,
                  'blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'sent': sent})


@require_POST
def post_comment(request, post_id):

    post = get_object_or_404(Post, id=post_id,
                             status=Post.Status.PUBLISHED)

    form = CommentForm(data=request.POST)
    comment = None

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request,
                  'blog/post/comment.html',
                  {'form': form,
                   'comment': comment,
                   'post': post})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    # to check if the form is submitted...
    # we check for the query parameter...
    # in the request.GET dictionary
    if 'query' in request.GET:
        # the form will be submitted using get
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # title matches will prevail over body matches
            search_vector = SearchVector('title', weight="A") + \
                SearchVector('body', weight="B")
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query))\
                .filter(rank__gte=0.3).order_by('-rank')

    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
