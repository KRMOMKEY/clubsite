from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),   # 🔥 홈 추가

    path('board/', views.board),
    path('create-post/', views.create_post),
    path('delete-post/<int:post_id>/', views.delete_post),
    path('edit-post/<int:post_id>/', views.edit_post),
    path('delete-comment/<int:comment_id>/', views.delete_comment),
    path('ranking/', views.ranking),

    path('post/<int:post_id>/', views.post_detail),

    path('comment/<int:post_id>/', views.add_comment),
    path('comment-like/<int:comment_id>/', views.like_comment),
    path('post-like/<int:post_id>/', views.like_post),
    path('vote-post/<int:post_id>/', views.vote_post),
    path('signup/', views.signup),
    path('profile/', views.profile),
    path('hide-post/<int:post_id>/', views.hide_post),
    path('unhide-post/<int:post_id>/',views.unhide_post),
    path('game1/', views.game1),
    path('game2/', views.game2),
    path('game3/', views.game3),
]
