from django.db import models

class Users(models.Model):    
    choices = (
        (1, 'SP'),
        (2, 'Administrator'),
        (3, 'Normal'),
    )
    type_user = models.CharField(max_length=6, choices=choices)  
    username = models.CharField(unique=True,max_length=50)
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True, max_length=200, null=True)
    code_referral = models.TextField(null=True, unique=True)
    invitation_id = models.CharField(null=True,max_length=200)
    language = models.TextField(default='en')
    referral = models.ManyToManyField('self', blank=True, symmetrical=False, through='RelationRef')
    wallet = models.CharField(null=True,max_length=200, unique=True)
    wallet_sp = models.TextField(null=True)
    acumulated_ref = models.FloatField(default=0.0)
    acumulated_nft = models.FloatField(default=0.0)
    connection = models.CharField(null=True,max_length=200)
 
class RelationRef(models.Model):
    from_usuario = models.ForeignKey(Users, related_name='relacion_referidos_from', on_delete=models.CASCADE)
    to_usuario = models.ForeignKey(Users, related_name='relacion_referidos_to', on_delete=models.CASCADE)
    extra_field = models.CharField(max_length=100)  # Campo adicional que deseas agregar
    
class CodeMail(models.Model):
    user_mail = models.EmailField(unique=True,max_length=100, null=True)
    code = models.CharField(max_length=6)
    status = models.BooleanField(default=True)
    registration_code= models.DateField(auto_now_add=True)
    
class BlackListedToken(models.Model):
    token = models.CharField(max_length=800)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE, unique=True)
    
class Pqrs(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    choices_category = (
        (1, 'Petición'),
        (2, 'Quejas'),
        (3, 'Reclamos'),
        (4, 'Sugerencias')
    )
    category = models.CharField(max_length=6, choices=choices_category,null=False)
    choices_status = (
        (1, 'Abierto'),
        (2, 'En Proceso'),
        (3, 'Cerrado')
    )
    status = models.CharField(max_length=6, choices=choices_status,null=False)
    status_noti = models.BooleanField(default=False)
    name_pqrs = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Messages(models.Model):
    pqrs = models.ForeignKey(Pqrs, on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    contents = models.CharField(max_length=200,null=True)
    img = models.CharField(max_length=400,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    img_key = models.CharField(max_length=400,null=True)
    
class Notifications(models.Model):
    status = models.CharField(max_length=200, null=True)
    subject = models.CharField(max_length=200, null=True)
    text_notification = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=200, null=True)
    status_icon = models.CharField(max_length=200, null=True)
    date_notification = models.DateField(auto_now_add=True, blank=True)
    user = models.ForeignKey(Users,on_delete=models.CASCADE, null=True)
    support = models.BooleanField(default=False, null=True)

class Academy(models.Model):
    choice_type_document=(
        (1,'pdf'),
        (2,'doc'),
        (3,'xlsx'),
        (4,'ppt'),
        (5,'cursos'),
        (6, 'audio'),
        
    )  
    title= models.CharField(max_length=150)
    language= models.CharField(max_length=50)
    img= models.CharField(max_length=400,null=True)
    key_img= models.CharField(max_length=200, null=True)
    type_document= models.CharField(max_length=8,choices=choice_type_document)
    description= models.CharField(max_length=250, null=True)
    created = models.DateTimeField(auto_now_add=True)
    key_file=models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=200, null= True)
    time_audio = models.CharField(max_length=200, null=True)
    user= models.ForeignKey(Users, on_delete=models.CASCADE)
    
class Series(models.Model):
    title= models.CharField(max_length=200,null=True)
    img= models.CharField(max_length=400,null=True)
    key_img= models.CharField(max_length=200, null=True)
    chapter = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    key_url = models.CharField(max_length=200, null=True)
    description= models.CharField(max_length=500, null=True)
    academy= models.ForeignKey(Academy, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)