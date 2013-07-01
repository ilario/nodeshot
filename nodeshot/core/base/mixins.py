"""
useful mixins that can be added to views
"""

from rest_framework.response import Response


class ACLMixin(object):
    """ implements ACL in views """
    
    def get_queryset(self):
        """
        Returns only objects which are accessible to the current user.
        If user is not authenticated all public objects will be returned.
        
        Model must implement AccessLevelManager!
        """
        return self.queryset.accessible_to(user=self.request.user)


class CustomDataMixin(object):
    """
    Implements custom data in views
    
    Must implement:
        * self.serializer_custom_class: a custom serializer
        * self.get_custom_data(): method that specifies the custom data to pass to the custom serializer
    """
    
    def get_custom_serializer(self, **kwargs):
        """ returns the custom serializer class """
        try:
            serializer_class = self.serializer_custom_class
        except AttributeError:
            serializer_class = self.get_serializer
        
        return serializer_class(**kwargs)
    
    def create(self, request, *args, **kwargs):
        """ custom create method """
        # copy request.DATA
        data = request.DATA.copy()
        
        # get the additional data
        additional_data = self.get_custom_data()
        
        # merge the two
        custom_data = dict(data.items() + additional_data.items())
        
        # pass custom data to serializer_custom_class
        serializer = self.get_custom_serializer(data=custom_data, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)

        return Response(serializer.errors, status=400)