from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # This method should be overriden
    # if we dont want to modify query set based on current instance attributes
    def get_queryset(self):
        """RETURN OBJECTS FOR THE CURRENT AUTHENTICATED USER ONLY"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # override this method for CreateModelMixin
    # create operation is done here (unlike in UserModelSerializer)
    # because serializer does not have user
    # we pass user to serializer and save it
    def perform_create(self, serializer):
        """CREATE A NEW TAG"""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet, 
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the databases"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self,serializer):
        """Create a new Ingredient"""
        serializer.save(user=self.request.user)

    

