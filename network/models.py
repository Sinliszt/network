from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

    @property
    def likes_count(self):
        return self.likes.count()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete = models.CASCADE, related_name="following_rel")
    following = models.ForeignKey(User, on_delete = models.CASCADE, related_name="followers_rel")

    class Meta:
        unique_together = ('following', 'follower')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

