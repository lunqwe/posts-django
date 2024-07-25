from django.urls import path
from .views import CreatePostView, RetrievePostView, ListPostView, UpdatePostView, DeletePostView

urlpatterns = [
    path('create/', CreatePostView.as_view(), name='create-post'),
    path('details/<int:id>/', RetrievePostView.as_view(), name='post-details'),
    path('list/', ListPostView.as_view(), name='post-list'),
    path('update/<int:id>', UpdatePostView.as_view(), name='post-update'),
    path('delete/<int:id>', DeletePostView.as_view(), name='post-delete'),
    
]
