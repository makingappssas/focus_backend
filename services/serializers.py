from services.models import *
from rest_framework import serializers


class PqrsListSerializers(serializers.ModelSerializer):
    class Meta:
        model= Pqrs
        fields=('id','name_pqrs','category','status', 'user_id','status_noti')

class SeriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields=('id','description','title','img','url','created')
#################################Academy##########################
class AcademySerializers(serializers.ModelSerializer):
    class Meta:
        model = Academy
        fields=('__all__')
        
class NotificationSerlializers(serializers.ModelSerializer):
    class Meta:
        model=Notifications
        fields=('__all__')