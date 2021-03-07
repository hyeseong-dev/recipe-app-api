from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BaseRecipeAttr(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes=(TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # This method should be overriden
    # if we dont want to modify query set based on current instance attributes
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # override this method for CreateModelMixin
    # create operation is done here (unlike in UserModelSerializer)
    # because serializer can not have user
    # we pass user to serializer and save it
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TagViewSet(BaseRecipeAttr):
    """manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttr):
    """Manage ingredients in the databases"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the databases"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)