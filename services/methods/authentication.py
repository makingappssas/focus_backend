from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from services.methods.mail import change_password_mail, mail_standar
from services.models import BlackListedToken, CodeMail, Users
from services.ServicesClass import AuthenticationClass, ClassTokens, StandarClass
from services.translations.en import en
from services.translations.es import es
from django.conf import settings

@csrf_exempt
def registration(request):
    if request.method != "POST":return JsonResponse({"ok":False,"error":"Allowe only method POST"},status=401,safe=False)
    valid = AuthenticationClass.recaptcha(request.headers)

    if valid != True: 
        return JsonResponse(AuthenticationClass._recaptcha, status=401, safe = False)

    data= JSONParser().parse(request)

    if Users.objects.filter(username = data['username']).exists() == True:
        return JsonResponse({"ok":False,"error":"Este usuario ya se encuentra registrado"},status=403,safe=False)

    if Users.objects.filter(email = data['email'].lower()).exists() == True:
        return JsonResponse({"ok":False,"error":"El correo ya se encuentra registrado en otra cuenta"},status=403,safe=False)

    if not CodeMail.objects.filter(code = data['code']).exists():
        return JsonResponse({"ok":False,"error":"código incorrecto"}, status= 403, safe=False)

    if not CodeMail.objects.filter(user_mail = data['email'].lower(), status=True).exists():
        return JsonResponse({"ok":False,"error":"Este código ya expiro o fue usado, solicita otro."}, status= 403, safe=False)

    CodeMail.objects.filter(user_mail = data['email'].lower()).update(status=False)
    del data['code']
    ref = False
    if data['code_referral'] is not None:
        ref = True
        user_1=Users.objects.get(code_referral=data['code_referral'] )
        data['invitation_id'] = user_1.pk
    data['code_referral'] = StandarClass.generete_code()
    data['password'] = make_password(data['password'])
    data['email'] = data['email'].lower()
    data['type_user'] = 3
    user = Users.objects.create(**data)
    if ref:
        user_1.referral.add(user)

    data = ClassTokens(user=user.pk).creaction_token()
    return JsonResponse({"ok":True, "data":data})

        


@csrf_exempt
def login(request):
    
    if request.method != "POST":
        return JsonResponse({"ok":False,"error":"Allowe only method POST"},status=401,safe=False)
    
    valid = AuthenticationClass.recaptcha(request.headers)
    if valid != True: 
        return JsonResponse(AuthenticationClass._recaptcha, status=401, safe = False)
    
    data= JSONParser().parse(request)
    if Users.objects.filter(username = data['username']).exists() != True:
        return JsonResponse({"ok":False,"error":"Este usuario no se encuentra registrado"},status=403,safe=False)
    
    user=Users.objects.get(username = data['username'])
    
    if "language" in data:
        user.language = data['language']
        user.save()
        
    if check_password(data['password'], user.password) != True:
        return JsonResponse({"ok":False,"error":"Contraseña incorrecta"}, status = 403, safe=False)
    
    data = ClassTokens(user=user.pk).creaction_token()
    return JsonResponse({"ok":True, "data":data})

@csrf_exempt
def create_sp_admin(request):
    if request.method != "ACCOUNT":
        return JsonResponse({"ok":False,"error":"Allowe only method ACCOUNT"},status=401,safe=False)
    
    if request.headers['host'].split(':')[0]!="127.0.0.1":
        return JsonResponse(AuthenticationClass._permissions,status = 401, safe=False)
    try:
        if not Users.objects.filter(username='superadmin').exists(): 
        # Crear usuario SP
            Users.objects.create(
                type_user=1,
                username='superadmin',
                email = 'ceo@makingapps.com.co',
                password=make_password('8Tx15@#55t@b&XWDgh1'),
                wallet=None
            )
        if not Users.objects.filter(username='admin').exists(): 

            # Crear usuario Administrator
            Users.objects.create(
                type_user=2,
                username='admin',
                email = settings.EMAIL_HOST_USER,
                password=make_password('p50D82#agW3!gJU0a*4')
            )
        return JsonResponse("created", safe=False)
    except:
        return JsonResponse("already exist", safe=False)


@csrf_exempt
def get_code(request):
    languages = {"es":es(),"en":en()}
    if request.method == "POST":
        valid = AuthenticationClass.recaptcha(request.headers)
        
        if valid != True: 
            return JsonResponse(AuthenticationClass._recaptcha, status=401, safe = False)
        
        data=JSONParser().parse(request)
        
        if Users.objects.filter(username = data['username']).exists() == True:
            return JsonResponse({"ok":False,"error":"Este usuario ya se encuentra registrado"},status=403,safe=False)
    
        if Users.objects.filter(email=data['email'].lower()).exists():
            return JsonResponse({"ok":False,"error":"Este correo ya se encuentra registrado"},status=403,safe=False)
        
        if CodeMail.objects.filter(user_mail=data['email'].lower()).exists()==True:
            CodeMail.objects.filter(user_mail=data['email'].lower()).delete()
            
        query = CodeMail.objects.create(user_mail=data['email'].lower(),code =StandarClass.random_number(),status=True )
        result=StandarClass.from_send_mail(self=data['email'].lower(),html_content=mail_standar(rando=query.code, language = 'en'), subject="Welcome")
        
        if result=="ok":
            return JsonResponse({"ok":True,"data":"El código de verificación ha sido enviado a correo"},status=200,safe=False)
        
        return JsonResponse({"ok":False,"error":"Ha ocurrido un error, intenta mas tarde"},status=403,safe=False)
    
    if request.method == "PUT":
        data=JSONParser().parse(request)

        if not Users.objects.filter(email=data['email'].lower()).exists():
            return JsonResponse({"ok":False,"error":"Este correo no se encuentra registrado"},status=403,safe=False)
        user = Users.objects.get(email=data['email'].lower())
        
        if CodeMail.objects.filter(user_mail=data['email'].lower()).exists()==True:
            CodeMail.objects.filter(user_mail=data['email'].lower()).delete()
            
        query = CodeMail.objects.create(user_mail=data['email'].lower(),code =StandarClass.random_number(),status=True )
        result=StandarClass.from_send_mail(self=data['email'].lower(),html_content=change_password_mail(rando=query.code, language = user.language), subject = languages[user.language]["Código de verificación"])
        
        if result=="ok":
            return JsonResponse({"ok":True,"data":"El código de verificación ha sido enviado a correo"},status=200,safe=False)
        
        return JsonResponse({"ok":False,"error":"Ha ocurrido un error, intenta mas tarde"},status=403,safe=False)
    
    if request.method=="GET":
        
        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: return JsonResponse(auth, status=401, safe=False)
        
        if CodeMail.objects.filter(user_mail=auth['data'].email).exists()==True:
            CodeMail.objects.filter(user_mail=auth['data'].email).delete()
        user = Users.objects.get(email=auth['data'].email)
        query = CodeMail.objects.create(user_mail=auth['data'].email, code =StandarClass.random_number(), status=True)
        result=StandarClass.from_send_mail(self=auth['data'].email, html_content=change_password_mail(rando=query.code, language = user.language), subject = languages[user.language]["Código de verificación"])
        
        if result=="ok":
            return JsonResponse({"ok":True,"data":"El código de verificación ha sido enviado a correo"},status=200,safe=False)
        
        return JsonResponse({"ok":False,"error":"Ha ocurrido un error, intenta mas tarde"},status=403,safe=False)
    return JsonResponse({"ok":False,"error":"Allowe only method POST,GET and PUT"},status=404,safe=False) 

@csrf_exempt
def change_code_mail(request):
    
    if request.method !="POST":
        return JsonResponse({"ok":False,"error":"Allowe only method GET"},status=404,safe=False) 
    
    data=JSONParser().parse(request)
    code = StandarClass.random_number()
    
    CodeMail.objects.update_or_create(user_mail=data['email'].lower(), defaults= {"code":code,"status":True} )
    
    result=StandarClass.from_send_mail(self=data['email'].lower(),html_content=mail_standar(rando=code, language="en"), subject="Bienvenido")
    
    if result=="ok":
        return JsonResponse({"ok":True,"data":"El código de verificación ha sido enviado a correo"},status=200,safe=False)
    
    return JsonResponse({"ok":False,"error":"Ha ocurrido un error, intenta mas tarde"},status=403,safe=False)

@csrf_exempt
def change_password(request):
    if request.method == "POST":
        valid = AuthenticationClass.recaptcha(request.headers)
        if valid != True: 
            return JsonResponse(AuthenticationClass._recaptcha, status=401, safe = False)
        
        data=JSONParser().parse(request)
        
        if not CodeMail.objects.filter(code = data['code']).exists():
            return JsonResponse({"ok":False,"error":"código incorrecto"}, status= 403, safe=False)
        
        if not CodeMail.objects.filter(user_mail = data['email'].lower(), status=True).exists():
            return JsonResponse({"ok":False,"error":"Este código ya expiro o fue usado, solicita otro."}, status= 403, safe=False)
        
        Users.objects.filter(email = data['email'].lower()).update(password = make_password(data['password']))
        
        CodeMail.objects.filter(user_mail = data['email'].lower(), status=True).update(status=False)
        return JsonResponse({"ok":True,"data":"Contraseña cambiada"},status=201, safe=False)

    if request.method == "PUT":
        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        
        data=JSONParser().parse(request)
        if not CodeMail.objects.filter(user_mail = auth['data'].email, status=True).exists():
            return JsonResponse({"ok":False,"error":"Este código ya expiro o fue usado, solicita otro."}, status= 403, safe=False)
        
        if not CodeMail.objects.filter(code = data['code']).exists():
            return JsonResponse({"ok":False,"error":"código incorrecto"}, status= 403, safe=False)
        
        Users.objects.filter(id = auth['data'].pk).update(password = make_password(data['password']))
        CodeMail.objects.filter(user_mail = auth['data'].email, status=True).update(status=False)
        return JsonResponse({"ok":True,"data":"Contraseña cambiada"},status=201, safe=False)
    
    return JsonResponse({"ok":False,"error":"Allowe only method POST and PUT"},status=404,safe=False)
    
@csrf_exempt  
def log_out(request):
    """
    Request encargada cerrar la sesión desde la plataforma 
    """
    if request.method!='GET':
        return JsonResponse({"ok":False,"error":"Allowe only method GET"},status=404,safe=False) 
    
    auth = AuthenticationClass.autohorization(request.headers)

    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    
    BlackListedToken.objects.filter(user_id = auth['data'].pk).update(status = False)
    return JsonResponse({"ok": True, "data":"logOut"},status=201,safe=False)

@csrf_exempt
def language_update(request):
    if request.method!='POST':
        return JsonResponse({"ok":False,"error":"Allowe only method POST"},status=404,safe=False) 
    
    auth = AuthenticationClass.autohorization(request.headers)

    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)

    Data = JSONParser().parse(request)
    auth['data'].language = Data['language']
    auth['data'].save()
    return JsonResponse({"ok":True,"data":"update language"})

@csrf_exempt
def get_users(request):
    
    if request.method!='GET':
        return JsonResponse({"ok":False,"error":"Allowe only method GET"},status=404,safe=False) 
    
    auth = AuthenticationClass.autohorization(request.headers)
    
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    
    if int(auth['data'].type_user) !=2:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 
    return JsonResponse({"ok":True,"data":list(Users.objects.all().order_by('-id').exclude(type_user__in= [1,2]).values('id','username'))})
