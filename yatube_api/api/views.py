from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, serializers, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.pagination import CustomPagination
from api.permissions import AuthorOrReadOnly, UserIsAuthenticated
from api.serializers import (CommentSerializer, FollowSerializer,
                             GroupSerializer, PostSerializer)
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, AuthorOrReadOnly]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, AuthorOrReadOnly]
    pagination_class = CustomPagination

    def get_post(self):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, id=post_id)

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [UserIsAuthenticated]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        following_username = self.request.data.get('following')
        following_user = User.objects.get(username=following_username)

        if user == following_user:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя.'
            )

        if Follow.objects.filter(user=user, following=following_user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )

        serializer.save(user=user, following=following_user)
