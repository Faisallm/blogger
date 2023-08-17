from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset() \
            .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    # dropdown selection option
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    tags = TaggableManager()
    # the default manager
    objects = models.Manager()
    # our custom manager
    published = PublishedManager()

    class Meta:
        # most recent posts at the top
        ordering = ('-publish',)
        # this will improve database query performance
        # since posts will be ordered by publish date.
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[
                           self.publish.year,
                           self.publish.month,
                           self.publish.day,
                           self.slug
                       ])


class Comment(models.Model):

    # post.comments.all()
    # ManyToOneField() a post can have multiple...
    # comments but each comment is only associated with...
    # one post 
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    # name of the user writhing comment
    name = models.CharField(max_length=80)
    # his email
    email = models.EmailField()
    # main text of the comment
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # whether comment is active or not.
    active = models.BooleanField(default=True)

    class Meta:
        # older posts at the top
        ordering = ('created',) 
        # so as to improve query performance...
        # from database
        indexes = [
            models.Index(fields=['created']),
        ] 

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"