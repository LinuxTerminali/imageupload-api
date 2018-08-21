from rest_framework import serializers
from .models import ImageUpload


class FileSerializer(serializers.ModelSerializer):
    '''
    A common serialzer for all the queries related to
    Imageupload Model 
    '''

    def to_representation(self, instance):
        '''
        Returns a complete url of uploaded
        image for the representations purpose 
        in response
        '''
        representation = super(
            FileSerializer, self).to_representation(instance)
        domain_name = "http://localhost:8000"
        full_path = domain_name + instance.file.url
        representation['file'] = full_path
        return representation

    class Meta():
        model = ImageUpload
        fields = ('id', 'file', 'title', 'description',
                  'timestamp', 'owner', 'shared')

