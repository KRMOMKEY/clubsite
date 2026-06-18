from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Score, Comment, CommentLike, Post, PostLike
from .models import Post, PostVote
from django.contrib.auth import login

# ----------------------
# 점수
# ----------------------
@login_required
def submit_score(request):
    if request.method == "POST":
        score = int(request.POST.get("score", 0))

        Score.objects.create(
            user=request.user,
            score=score
        )

        return JsonResponse({"status": "ok"})


# ----------------------
# 홈
# ----------------------
@login_required
def home(request):

    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()

    hot_posts = Post.objects.order_by(
        '-score',
        '-views'
    )[:10]
    notices = Post.objects.filter(
    is_notice=True
    ).order_by('-created_at')[:5]

    return render(request, "home.html", {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "hot_posts": hot_posts,
        "notices": notices,
    })

# ----------------------
# 랭킹
# ----------------------
def ranking(request):
    scores = Score.objects.order_by('-score')
    return render(request, 'ranking.html', {'scores': scores})


# ----------------------
# 게시판 (검색 + 인기순 + 최신 + 페이지네이션 + 공지)
# ----------------------
def board(request):
    sort = request.GET.get('sort', 'hot')
    query = request.GET.get('q', '')
    page = request.GET.get('page')

    posts = Post.objects.filter(
    is_hidden=False
    )
    
    

    # 🔍 검색
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        )

    # 🔥 Reddit 스타일 정렬
    if sort == 'hot':
        posts = posts.annotate(
            hot_score=F('score') + F('views') * 0.1
        ).order_by('-is_notice', '-hot_score', '-created_at')

    elif sort == 'top':
        posts = posts.order_by('-is_notice', '-score')

    else:
        posts = posts.order_by('-is_notice', '-created_at')

    paginator = Paginator(posts, 10)
    Post.objects.filter(is_hidden=False)

    return render(request, 'board.html', {
        'posts': posts,
        'sort': sort,
        'query': query
    })


# ----------------------
# 글 작성
# ----------------------
@login_required
def create_post(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title or not content:
            return redirect('/board/')

        is_notice = False

        if request.user.is_staff:
            is_notice = request.POST.get("is_notice") == "on"

        Post.objects.create(
            user=request.user,
            title=title,
            content=content,
            is_notice=is_notice
        )

        return redirect('/board/')

    return redirect('/board/')

# ----------------------
# 게시글 상세
# ----------------------
def post_detail(request, post_id):
    Post.objects.filter(id=post_id).update(views=F('views') + 1)

    post = get_object_or_404(Post, id=post_id)
    comments = post.comment_set.filter(parent=None)

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments
    })


# ----------------------
# 댓글 작성
# ----------------------
@login_required
def add_comment(request, post_id):

    if request.method == "POST":

        content = request.POST.get("content", "").strip()

        parent_id = request.POST.get("parent_id")

        parent = None

        if parent_id:
            parent = Comment.objects.get(id=parent_id)

        if content:

            comment = Comment.objects.create(
                post_id=post_id,
                user=request.user,
                content=content,
                parent=parent
            )

            return JsonResponse({
                "success": True,
                "id": comment.id,
                "username": request.user.username,
                "content": comment.content
            })

    return JsonResponse({
        "success": False
    })

# ----------------------
# 게시글 좋아요
# ----------------------
@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)

    like, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect('/board/')


# ----------------------
# 댓글 좋아요
# ----------------------
@login_required
def like_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)

    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect('/board/')


# ----------------------
# 게시글 삭제
# ----------------------
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.user or request.user.is_staff:
        post.delete()

    return redirect('/board/')


# ----------------------
# 게시글 수정
# ----------------------
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user:
        return redirect('/board/')

    if request.method == "POST":
        post.title = request.POST.get("title", "").strip()
        post.content = request.POST.get("content", "").strip()

        post.edited = True
        post.edited_at = timezone.now()
        post.save()

        return redirect(f'/post/{post.id}/')

    return render(request, 'edit_post.html', {
        'post': post
    })


# ----------------------
# 댓글 삭제
# ----------------------
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user:
        post_id = comment.post.id
        comment.delete()
        return redirect(f'/post/{post_id}/')

    return redirect('/board/')

@login_required
def vote_post(request, post_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False
        })

    post = get_object_or_404(Post, id=post_id)

    value = int(request.POST.get("value", 0))

    if value not in [1, -1]:
        return JsonResponse({
            "success": False
        })

    vote, created = PostVote.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={
            "value": value
        }
    )

    if created:

        post.score += value

    else:

        if vote.value == value:

            post.score -= vote.value
            vote.delete()

        else:

            post.score -= vote.value

            vote.value = value
            vote.save()

            post.score += value

    post.save()

    return JsonResponse({
        "success": True,
        "score": post.score
    })

def signup(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            return render(request, "signup.html", {
                "error": "모든 항목을 입력하세요."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "이미 존재하는 아이디입니다."
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, "signup.html")


@login_required
def profile(request):

    user_posts = Post.objects.filter(
        user=request.user
    ).count()

    user_comments = Comment.objects.filter(
        user=request.user
    ).count()

    return render(request, "profile.html", {
        "user_posts": user_posts,
        "user_comments": user_comments,
    })


@login_required
def profile(request):

    my_posts = Post.objects.filter(
        user=request.user
    ).order_by('-created_at')

    my_comments = Comment.objects.filter(
        user=request.user
    )

    total_score = sum(
        post.score for post in my_posts
    )

    return render(request, 'profile.html', {
        'my_posts': my_posts[:10],
        'post_count': my_posts.count(),
        'comment_count': my_comments.count(),
        'total_score': total_score,
    })

@login_required
def promote_user(request, user_id):

    if not request.user.is_superuser:
        return redirect('/')

    user = User.objects.get(id=user_id)

    user.is_staff = True
    user.save()

    return redirect('/admin-panel/')

@login_required
def demote_user(request, user_id):

    if not request.user.is_superuser:
        return redirect('/')

    user = User.objects.get(id=user_id)

    user.is_staff = False
    user.save()

    return redirect('/admin-panel/')

@login_required
def hide_post(request, post_id):

    if not request.user.is_staff:
        return redirect('/')

    post = get_object_or_404(
        Post,
        id=post_id
    )

    post.is_hidden = True
    post.save()

    return redirect('/board/')

@login_required
def unhide_post(request, post_id):

    if not request.user.is_staff:
        return redirect('/')

    post = get_object_or_404(
        Post,
        id=post_id
    )

    post.is_hidden = False
    post.save()

    return redirect('/board/')


def game1(request):
    return render(request, "games/program1.html")


def game2(request):
    return render(request, "games/program2.html")


def game3(request):
    return render(request, "games/program3.html")
