from django.db import models
from django.contrib.auth.models import User


# 🎮 게임 점수
class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"


# 🧠 문제 (유지용)
class Problem(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    answer = models.CharField(max_length=100)
    point = models.IntegerField(default=100)

    def __str__(self):
        return self.title


# 📤 제출
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    submitted_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)


# 💬 게시글
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    views = models.PositiveIntegerField(default=0)

    is_notice = models.BooleanField(default=False)

    # 🔥 Reddit 핵심: 점수 시스템
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# 💬 댓글 (대댓글 포함)
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    def __str__(self):
        return self.content


# ❤️ 댓글 좋아요
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('comment', 'user')

class PostLike(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')  # 1명 1좋아요


class PostVote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField()  # +1 = 좋아요, -1 = 싫어요

    class Meta:
        unique_together = ('post', 'user')
