from django import template
from ..models import Post
from django.db.models import Count


register = template.Library()


# simple tag processes the data and returns a string
@register.simple_tag
def total_posts():
    return Post.published.count()


# inclusion tag processes the data and returns a rendered template
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_post(count=5):
    # annotate is used to aggregate the number of comments...
    # for each posts and ordering my the posts with...
    # post with the most comments at the top.
    return Post.published.annotate(total_comments=Count('comments'))\
        .order_by('-total_comments')[:count]

