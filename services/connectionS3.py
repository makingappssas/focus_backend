from os import remove
import boto3
import datetime
from hashlib import blake2b
import random
import shutil
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from services.models import *

  
class FilesS3():
    def __init__(self, resource = None, key = None) -> None:
        self.bucket = settings.BUCKET_NAME
        self.resource = resource
        self.key = key
        self.s3 = boto3.client('s3', region_name='us-east-3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


    def file_upload(self):
        """
        Carga un archivo al bucket de S3, elimina el archivo local y devuelve la URL del archivo en el bucket.
        :return: La URL del archivo cargado en el bucket.
        """
        self.s3.upload_file(self.resource, self.bucket, self.key)
        remove(self.resource)
        return self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': self.key}, ExpiresIn = 3600)
    
    
    def file_upload_nft(self):
        """
        Carga un archivo al bucket de S3, elimina el archivo local y devuelve la URL del archivo en el bucket.
        :return: La URL del archivo cargado en el bucket.
        """
        self.s3.upload_file(self.resource, self.bucket, self.key, ExtraArgs={'ACL': 'public-read'})
        remove(self.resource)
        return f"https://focusnft.s3.us-east-2.amazonaws.com/{self.key}"


    def refresh(self):
        """
        Obtiene la URL del archivo en el bucket sin cargarlo nuevamente.
        :return: La URL del archivo en el bucket.
        """
        return self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': self.key}, ExpiresIn = 3600)

    
    def delete_file(self):
        """
        Elimina el archivo del bucket.
        """ 
        self.s3.delete_object(Bucket=self.bucket, Key=self.key)


    def download_file(self):
        """
        Descargar el archivo del bucket.
        """
        self.s3.download_file(Bucket=self.bucket, Key=self.key, Filename=f'media/{self.key}')

class StandarClass:
    def generate_certification_filename(self):
        original_filename = self.name
        extension = original_filename.split('.')[-1]
        name = blake2b(digest_size=8)
        name.update(
            bytes(
                str(datetime.datetime.now(datetime.timezone.utc)), encoding="utf-8"
            )
        )
        name.update(bytes(str(random.randint(1, 999999)), encoding="utf-8"))
        return f"{name.hexdigest()}.{extension}"    

    def upload_certification_file(self):
        new_filename = StandarClass.generate_certification_filename(self)

        # Guardar el archivo en una carpeta temporal
        temp_path = f"media/{new_filename}"
        with open(temp_path, 'wb') as temp_file:
            shutil.copyfileobj(self.file, temp_file)

        # Cargar el archivo en S3 y obtener la URL
        url = FilesS3(resource=temp_path, key=new_filename).file_upload()
        return url, new_filename   
    
    def upload_nft(self):
        new_filename = StandarClass.generate_certification_filename(self)

        temp_path = f"media/{new_filename}"
        with open(temp_path, 'wb') as temp_file:
            shutil.copyfileobj(self.file, temp_file)

        # Cargar el archivo en S3 y obtener la URL
        return FilesS3(resource=temp_path, key=new_filename).file_upload_nft()
   
    
    def from_send_mail(self, subject, html_content):
        """
        Función encargada mandar correos electrónicos.
        """
        msg = EmailMultiAlternatives(
            subject, strip_tags(html_content), settings.EMAIL_HOST_USER, [self]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return "ok"

    def from_send_mail_file(self, subject, html_content, path_file):
        """
        Función encargada mandar correos electrónicos.
        """
        msg = EmailMultiAlternatives(
            subject, strip_tags(html_content), settings.EMAIL_HOST_USER, [self]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.attach_file(path_file)
        msg.send()
        return "ok"