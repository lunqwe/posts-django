from django.urls import path

from .views import CreateCommentView, RetrieveCommentView, ListCommentView, UpdateCommentView, DeleteCommentView

urlpatterns = [
    path('create/', CreateCommentView.as_view(), name='create-comment'),
    path('get/<int:id>', RetrieveCommentView.as_view(), name='retrieve-comment'),
    path('list/', ListCommentView.as_view(), name='list-comments'),
    path('update/<int:id>', UpdateCommentView.as_view(), name='update-comment'),
    path('delete/<int:id>', DeleteCommentView.as_view(), name='delete-comment'),
]
