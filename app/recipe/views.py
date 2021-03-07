from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        queryset = self.queryset
        if assigned_only:
            # Django also allows access of reverse relation in foreign keys
            queryset = queryset.filter(recipe__isnull=False)
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


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

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

    def _params_to_int(self, qs):
        """convert a list of string IDs to ints"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        # filtering based on params in payload
        # returns none if params are not available
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_int(tags)
            # djangos filter for attrs
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
            
        return self.serializer_class


    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe, 
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
