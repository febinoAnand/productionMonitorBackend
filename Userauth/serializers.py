from rest_framework import serializers
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

class UnauthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnauthUser
        fields = ('mobile_no','createdatetime','otp','emailaddress','session_id','device_id','otp_called','designation','is_existing_user','verification_token')
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

    
class UserDetailSerializer(serializers.ModelSerializer):
    usermod = UserSerializer(source="extUser", read_only=True)
    userdetail_id = serializers.IntegerField(source="id", read_only=True)
    user_id = serializers.IntegerField(source="extUser.id", read_only=True)
    userActive = serializers.BooleanField(source="extUser.is_active")

    class Meta:
        model = UserDetail
        fields = ('userdetail_id', 'user_id', 'usermod', 'designation', 'mobile_no', 'userActive')
    
    # def update(self, instance, validated_data):
    #     print("Starting update method")
    #     ext_user_data = validated_data.pop('extUser', None)
    #     print("Extracted ext_user_data:", ext_user_data)

    #     if ext_user_data:
    #         username = ext_user_data.get('username')
    #         user_instance = instance.extUser
    #         print("Current user instance:", user_instance)

    #         if username:
    #             print("Username provided:", username)
    #             # Check if the username belongs to another user
    #             existing_user = User.objects.filter(username=username).first()
    #             print("Existing user with the username:", existing_user)

    #             if existing_user and existing_user != user_instance:
    #                 print(f"Username {username} belongs to another user. Updating that user.")
    #                 # Update the existing user with the new details from ext_user_data
    #                 for attr, value in ext_user_data.items():
    #                     print(f"Updating {attr} for the existing user.")
    #                     setattr(existing_user, attr, value)
    #                 existing_user.save()
                    
    #                 # Reassign the UserDetail instance to the existing user
    #                 instance.extUser = existing_user
    #                 print("Reassigned UserDetail to the existing user.")
    #             else:
    #                 print(f"Username {username} belongs to the current user or no conflict found.")
    #                 # Update the current user instance with the new details
    #                 for attr, value in ext_user_data.items():
    #                     print(f"Updating {attr} for the current user.")
    #                     setattr(user_instance, attr, value)
    #                 user_instance.save()

    #     try:
    #         # Update the UserDetail fields
    #         result = super().update(instance, validated_data)
    #         print("UserDetail instance updated:", result)
    #         return result
    #     except Exception as e:
    #         print("Error during update:", str(e))
    #         raise e

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('all_user_expiry_time','OTP_resend_interval','OTP_valid_time','OTP_call_count','OTP_wrong_count')


        
class UserAuthAPISerializer(serializers.Serializer):
    appToken = serializers.UUIDField(required=True,allow_null=False)
    mobileno = serializers.CharField(required=True,max_length=15,allow_null=False)
    email = serializers.EmailField(required=True,allow_null=False)
    deviceID = serializers.UUIDField(required=True,allow_null=False)



class UserAuthPromptSerializer(serializers.Serializer):
    appToken = serializers.UUIDField(required=True,allow_null=False)
    sessionID = serializers.UUIDField(required=True,allow_null=False)
    deviceID = serializers.UUIDField(required=True,allow_null=False)
    needtochange = serializers.BooleanField(allow_null=False)
    # isExistingUser = serializers.BooleanField(allow_null=False)


class UserAuthVerifySerializer(serializers.Serializer):
    appToken = serializers.UUIDField(required=True,allow_null=False)
    sessionID = serializers.UUIDField(required=True,allow_null=False)
    OTP = serializers.DecimalField(required=True,max_digits=5,decimal_places=0,allow_null=False)
    deviceID = serializers.UUIDField(required=True,allow_null=False)



class UserAuthRegisterSerializer(serializers.Serializer):
    appToken = serializers.UUIDField(required=True,allow_null=False)
    sessionID = serializers.UUIDField(required=True,allow_null=False)
    deviceID = serializers.UUIDField(required=True,allow_null=False)
    designation = serializers.CharField(max_length=50, required=True,allow_null=False)
    name = serializers.CharField(max_length=30, required=True,allow_null=False)
    password = serializers.CharField(max_length=30, required=True,allow_null=False)
    notificationID = serializers.CharField(max_length=50, required=True,allow_null=False)


class UserAuthResendSerializer(serializers.Serializer):
    appToken = serializers.UUIDField(required=True,allow_null=False)
    sessionID = serializers.UUIDField(required=True,allow_null=False)
    deviceID = serializers.UUIDField(required=True,allow_null=False)



class UserSerializer(serializers.ModelSerializer):
    mobile_no = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'mobile_no']

    def get_mobile_no(self, obj):
        try:
            return obj.userdetail.mobile_no
        except UserDetail.DoesNotExist:
            return None

class AuthGroupSerializer(serializers.ModelSerializer):
    user_set = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_set', 'user_details']

    def get_user_details(self, obj):
        users = obj.user_set.all()
        user_serializer = UserSerializer(users, many=True)
        return user_serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_details'] = self.get_user_details(instance)
        return representation


class LoginSerializer(serializers.Serializer):
    app_token = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    device_id = serializers.CharField(required=True)
    notification_id = serializers.CharField(required=True)

class LogoutSerializer(serializers.Serializer):
    app_token = serializers.CharField()
    device_id = serializers.CharField()

  


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return data





class WebLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class WebLogoutSerializer(serializers.Serializer):
    token = serializers.CharField()

class AdminChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True)
   
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return data

class UserActivitySerializer(serializers.Serializer):
    username = serializers.CharField()

class UserStatusUpdateSerializer(serializers.Serializer):
    username = serializers.CharField()
    is_active = serializers.BooleanField()
    password = serializers.CharField(write_only=True)


class UserVerificationSerializer(serializers.Serializer):
    username = serializers.CharField()
    mobile_no = serializers.CharField(max_length=15)