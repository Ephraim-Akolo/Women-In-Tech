from rest_framework import generics, mixins, status, exceptions
from website.models import User
from .serializers import RegistrationFormSerializer

# Create your views here.


class RegistrationFormView(mixins.CreateModelMixin, mixins.UpdateModelMixin , generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationFormSerializer

    def get_object(self):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = self.queryset.get(email__iexact=self.request.data['email'])
        except User.DoesNotExist:
            raise exceptions.NotFound
        return user

    def put(self, request, *args, **kwargs):
        try:
            resp = self.update(request, *args, **kwargs)
        except exceptions.NotFound:
            resp = self.create(request, *args, **kwargs)
        return resp
