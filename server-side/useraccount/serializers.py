from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User, Contact

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'avatar_url', 'email', 'date_joined', 'last_login',
            'username', 'city', 'phone',  # new fields
        )


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ( 'id', 'name', 'email', 'query_text' )


class TigminoRegisterSerializer(RegisterSerializer):
    """Sign-up serializer that also saves the user's full name."""
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def custom_signup(self, request, user):
        user.name = self.validated_data.get('name', '')
        user.save(update_fields=['name'])
