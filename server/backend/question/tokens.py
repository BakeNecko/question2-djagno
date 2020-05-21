from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class ObtainTokenPair(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
