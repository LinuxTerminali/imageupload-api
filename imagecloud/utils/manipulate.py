import io
from io import BytesIO
import PIL
from PIL import Image
import requests
import tempfile
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from rest_framework.parsers import ParseError
from rest_framework.exceptions import UnsupportedMediaType


def download_image(url, resize, size):
    '''
    This functions downloads image from the given url and return back django image field
    instance
    '''
    absoulte_url = url.split('?')[0]
    url_schema = ["http", "https"]
    if url_schema[0] not in url:
        url = url_schema[0]+url
    try:
        r = requests.head(url)
    except:
        raise ParseError('Invalid url')
    if 'image' not in r.headers.get('content-type'):
        return ParseError('Invalid image type')
    else:
        try:
            image_file_path = absoulte_url.split('/')[-1]
            im = Image.open(requests.get(url, stream=True).raw)
            format = im.format
            if '.' not in image_file_path:
                image_file_path += "."+format
            if resize:
                return resizeImage(im, size, image_file_path, True)
            
            return createFieldImage(im, image_file_path, format)
        except Exception as e:
            raise ParseError('Invalid image type')


def encrypt_username(user_name, user_id):
    '''
    This function encrypt username using caesar cipher
    i.e used for creating seprate folder for each user
    '''
    result = ""
    for i in range(len(user_name)):
        char = user_name[i]
        if (char.isupper()):
            result += chr((ord(char) + user_id-65) % 26 + 65)
        else:
            result += chr((ord(char) + user_id - 97) % 26 + 97)
    return result


def resizeImage(file, size, filename,downloaded):
    '''
    This function take file and resize parameter and resize the image using 
    pillow.
    '''
    if downloaded:
        im = file
        format = im.format
    else:
        try:
            im = Image.open(file)
            im.verify()
        except:
            raise UnsupportedMediaType('Invalid Image type')    
        im = Image.open(file)
        format = im.format
    try:
        width, height = size.split('x')
        im = im.resize((int(width), int(height)), PIL.Image.ANTIALIAS)
    except:
        raise ParseError('Invalid resize value')
    return createFieldImage(im, filename, format)


def createFieldImage(im, filename, format):
    '''
    This function takes pillow image instance and converts it into django
    image field.
    '''
    try:
        imgByteArr = io.BytesIO()
        im = im.save(imgByteArr, format=format)
        imgByteArr = imgByteArr.getvalue()
        ok = ContentFile(imgByteArr)
        return InMemoryUploadedFile(ok, None, filename, 'image/'+format, ok.tell, None)
    except:
        raise ParseError('Failed to decode Image')
