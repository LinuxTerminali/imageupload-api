from django.shortcuts import render
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.social_serializers import TwitterLoginSerializer
from rest_auth.social_serializers import TwitterConnectSerializer
from rest_auth.registration.views import SocialConnectView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser, ParseError, JSONParser
from .models import ImageUpload
from .serializers import FileSerializer
from PIL import Image
from rest_framework import viewsets
from .utils import manipulate
import json
from coreapi.utils import File
import pandas as pd
from rest_framework.schemas import AutoSchema
from rest_framework import schemas
import coreapi
import coreschema


class TwitterLogin(SocialLoginView):
    '''
    User login using Twitter auth1.0
    '''
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


class TwitterConnect(SocialConnectView):
    '''
    User registration using Twitter auth1.0
    '''
    serializer_class = TwitterConnectSerializer
    adapter_class = TwitterOAuthAdapter


class FileView(APIView):
    def post(self, request, *args, **kwargs):
        '''
        Takes form data with field,title,description and shared as a parameter
        and returns back url and timestamp on success. Also requires authentication
        using jwt token pass authrization token in header
        with jwt and followed by token value.
        parameters:
        field
        - title: title
          description: title for the images
          required: true
          type: string
          paramType: text
        - description: description
          description: description for the images
          required: true
          paramType: text
        - field: field/image
          paramType: input file
        - shared: sharing
          description: boolean field for sharing the image
          required: false
          paramType: boolean
          default:false
        - resize: text
          description: parameter for resizing image
          required: false
          paramType: text
          example:720x1080
          default:false
        '''

        if "resize" in request.data:
            request.data['file'] = manipulate.resizeImage(
                request.data['file'], request.data['resize'], request.data['file'].name, False)
        request.data['owner'] = request.user.id
        file_serializer = FileSerializer(data=request.data)
        print(file_serializer)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLFileView(APIView):
    '''
        Takes json data with url,title,description and shared as variables
        and returns back url and timestamp on success. Also requires authentication
        using jwt token pass authrization token in header
        with jwt and followed by token value.
    '''
    def post(self, request, format=None):
        '''
        Takes json data with url,title,description and shared as variables
        and returns back url and timestamp on success. Also requires authentication
        using jwt token pass authrization token in header
        with jwt and followed by token value.
        parameters:
        field
        - title: title
          description: title for the images
          required: true
          type: string
          paramType: text
        - description: description
          description: description for the images
          required: true
          paramType: text
        - url: url
          paramType: text
        - shared: sharing
          description: boolean field for sharing the image
          required: false
          paramType: boolean
          default:false
        - resize: text
          description: parameter for resizing image
          required: false
          paramType: text
          example:720x1080
          default:None
        '''
        if 'resize' in request.data:
            request.data['file'] = manipulate.download_image(
                request.data['url'], True, request.data['resize'])
        else:
            request.data['file'] = manipulate.download_image(
                request.data['url'], False, None)
        request.data['owner'] = request.user.id
        file_serializer = FileSerializer(
            data=request.data, context={'request': request})
        print(file_serializer)
        print(request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiImageUpload(APIView):
    '''
    Handle multiple image upload at once using Form. Requires authentication
    using jwt token pass authrization token in header with jwt and followed by token value.
    '''
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        '''
        Takes form data with field,title,description and shared as a parameter
        and returns back url and timestamp on success. Also requires authentication
        using jwt token pass authrization token in header
        with jwt and followed by token value.
        parameters:
        field
        - title: title
          description: title for the images
          required: true
          type: string
          paramType: text
        - description: description
          description: description for the images
          required: true
          paramType: text
        - field: field/image
          paramType: input file
        - shared: sharing
          description: boolean field for sharing the image
          required: false
          paramType: boolean
          default:false
        - resize: text
          description: parameter for resizing image
          required: false
          paramType: text
          example:720x1080
          default:false
        '''

        print(request.data.getlist('field'))
        request.data['owner'] = request.user.id
        all_files = request.data.getlist('field')
        data = {}
        for index, file in enumerate(all_files):
            request.data['file'] = file
            file_serializer = FileSerializer(data=request.data)
            print(file_serializer)
            if file_serializer.is_valid():
                file_serializer.save()
                print(str(file_serializer.data))
                data_key = 'image'+str(index)
                data[data_key] = str(file_serializer.data)
            else:
                data["detail"] = file_serializer.errors
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data["detail"] = file_serializer.errors
        return Response(data, status=status.HTTP_201_CREATED)


class CsvUpload(APIView):
    '''
    Handle multiple image upload at once using csv containing direct urls of images. 
    Requires authentication using jwt token pass authrization token in header with
     jwt and followed by token value.
    '''
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        ''' 
        Csv file must contains key value title,description,url and shared        
        parameters:
        - field: field/image
          paramType: input file
        '''
        # print(request.data.getlist('field'))
        try:
            csv_file = request.data['field']
            print('csv_file')
            data = {}
            df_csv = pd.read_csv(csv_file)
            required_keys = ['title', 'description', 'url', 'shared']
            if (required_keys[0] not in df_csv) or (required_keys[1] not in df_csv) or (required_keys[2] not in df_csv) or (required_keys[3] not in df_csv):
                return Response({'detail': 'Invalid csv file'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            for index, row in df_csv.iterrows():
                modified_data = {}
                modified_data['owner'] = request.user.id
                modified_data['title'] = row['title']
                modified_data['url'] = row['url']
                modified_data['shared'] = row['shared']
                modified_data['description'] = row['description']
                modified_data['file'] = manipulate.download_image(
                    row['url'], False, None)
                file_serializer = FileSerializer(data=modified_data)
                print(file_serializer)
                if file_serializer.is_valid():
                    file_serializer.save()
                    print(str(file_serializer.data))
                    data_key = 'image'+str(index)
                    data[data_key] = str(file_serializer.data)
                else:
                    data["detail"] = file_serializer.errors
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            data["detail"] = file_serializer.errors
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'detail':'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)


class GetSharedImages(viewsets.ModelViewSet):
    """
    This view should return a list of images shared
    with the community.
    """
    queryset = ImageUpload.objects.filter(shared=True)
    serializer_class = FileSerializer
    http_method_names = ['get']


class GetUserImages(viewsets.ModelViewSet):
    """
    This view should return a list of all the images uploaded
    by the currently authenticated user.
    """
    http_method_names = ['get']
    serializer_class = FileSerializer

    def get_queryset(self):
        user = self.request.user
        return ImageUpload.objects.filter(owner=user)


class UpdateUserImages(APIView):
    """
    Retrieve, update or delete a images instance.
    """

    def get_object(self, pk):
        try:
            return ImageUpload.objects.get(pk=pk)
        except ImageUpload.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    serializer_class = FileSerializer

    def put(self, request, pk, format=None):
        """
         update images instance. Required all the required fields
         such as title,description and url 
        """
        user_images = self.get_object(pk)
        print(user_images.owner_id, pk)
        if user_images.owner_id == request.user.id:
            serializer = FileSerializer(user_images, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk, format=None):
        """
         update images instance. Required fields id in the query
        """
        user_images = self.get_object(pk)
        print(user_images.owner_id, request.user.id)
        if user_images.owner_id == request.user.id:
            serializer = FileSerializer(user_images, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, format=None):
        """
         Delete images instance. Required fields id in the query
        """
        user_images = self.get_object(pk)
        if user_images.owner_id == request.user.id:
            user_images = self.get_object(pk)
            user_images.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
