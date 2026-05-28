from django.contrib.auth import get_user_model
from django.http import JsonResponse
from djoser.serializers import UserSerializer
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, \
    ReadOnlyModelViewSet

from .permissions import IsAuthorOrReadOnly, IsOwner
from serializers import AvatarSerializer, UserProfileSerializer
from .serializers import RecipeSerializer, TagSerializer
from recipes.models import Recipe, Tag

User = get_user_model()

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='get_link/')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        host = self.request.build_absolute_uri()
        return JsonResponse(
            {'short-link': host + recipe.short_link},
            status=status.HTTP_200_OK)






class UserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                  mixins.UpdateModelMixin, GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'patch']

    @action(detail=False, methods=['put'], url_path='me/avatar/',
            serializer_class=AvatarSerializer,
            permission_classes=[IsOwner])
    def update_avatar(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.avatar = serializer.validated_data['avatar']
        request.user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='me/avatar/',
            permission_classes=[IsOwner])
    def delete_avatar(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)









# Create your views here.
