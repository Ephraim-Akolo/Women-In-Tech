from rest_framework import serializers
from website.models import User, RegisteredCourse
from .html import html


class RegistrationFormSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    age = serializers.IntegerField()
    uiux_design = serializers.BooleanField(default=False, write_only=True)
    data_analysis = serializers.BooleanField(default=False, write_only=True)
    reason = serializers.CharField(write_only=True, allow_blank=True)
    course = serializers.CharField(read_only=True)
    
    class Meta(object):
        model = User
        fields = ["first_name", "last_name", "email", "age", "uiux_design", "data_analysis", "reason", "course"]


    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        age = validated_data.pop('age')
        email = validated_data.pop('email')
        reason = validated_data.pop('reason')
        uiux_design = validated_data.pop('uiux_design')
        data_analysis = validated_data.pop('data_analysis')
        selected_course = self.get_selected_course(uiux_design=uiux_design, data_analysis=data_analysis)
        user = User.objects.create(email=email, first_name=first_name, last_name=last_name, age=age)
        reg_course = RegisteredCourse.objects.create(user=user, course=selected_course, reason=reason)
        user.course = reg_course.course
        sent, msg = user.email_user(subject="Women in Tech", message=html.format(name=f'{first_name} {last_name}', from_email='info@paritie.com'))
        if not sent:
            print(msg)
        return user
    
    def update(self, user:User, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        age = validated_data.pop('age')
        # email = validated_data.pop('email')
        reason = validated_data.pop('reason')
        uiux_design = validated_data.pop('uiux_design')
        data_analysis = validated_data.pop('data_analysis')
        selected_course = self.get_selected_course(uiux_design=uiux_design, data_analysis=data_analysis)
        user.first_name = first_name
        user.last_name = last_name
        user.age = age
        user.save()

        try:
            reg_course = RegisteredCourse.objects.get(user=user)
            reg_course.course = selected_course
            reg_course.reason = reason
            reg_course.save()
        except RegisteredCourse.DoesNotExist:
            reg_course = RegisteredCourse.objects.create(user=user, course=selected_course, reason=reason)
        user.course = reg_course.course
        sent, msg = user.email_user(subject="Women in Tech", message=html.format(name=f'{first_name} {last_name}', from_email='info@paritie.com'))
        if not sent:
            print(msg)
        return user
    
    def get_selected_course(self, uiux_design, data_analysis):
        if uiux_design is True and data_analysis is True:
            raise serializers.ValidationError("You can only register for one course!")
        elif uiux_design is False and data_analysis is False:
            raise serializers.ValidationError("You must register atleast one course! Set uiux_design or data_analysis to true!")
        elif uiux_design:
            return RegisteredCourse.Course.UIUX_DESIGN
        return RegisteredCourse.Course.DATA_ANALYSIS
