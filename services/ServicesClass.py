import datetime
from email.utils import formataddr
import http, http.client, json, jwt, random
import string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from services.models import BlackListedToken, CodeMail, Users

def json_convert(self):
    """
    Toma una lista de diccionarios, la convierte en una cadena, elimina el primer y el último
    carácter y luego la vuelve a convertir en un diccionario.
    :return: Los datos se devuelven en formato json.
    """
    """
    It takes a list of dictionaries, converts it to a string, removes the first and last characters,
    then converts it back to a dictionary
    :return: The data is being returned in a json format.
    """
    return self[0] if self else []
    

class StandarClass:
    logo_complete = 'https://paywithcryptoapp.com/api/media/mail/logo.png'
    logo_w = 'https://paywithcryptoapp.com/api/media/mail/logo_w.png'
    logo_navbar = 'https://paywithcryptoapp.com/api/media/mail/logo_navbar.png'
    logo_footer = 'https://paywithcryptoapp.com/api/media/mail/logo_footer.png'
    image_facebook = 'https://paywithcryptoapp.com/api/media/mail/facebook.png'
    image_instagram = 'https://paywithcryptoapp.com/api/media/mail/instagram.png'
    image_whatsapp = 'https://paywithcryptoapp.com/api/media/mail/whatsapp.png'
    
    def from_send_mail(self, subject, html_content):
        """
        Función encargada mandar correos electrónicos.
        """
        sender_formatted = formataddr(("Support Focus", settings.EMAIL_HOST_USER))
        msg = EmailMultiAlternatives(
            
            subject, strip_tags(html_content), sender_formatted, [self]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return "ok"
    
    def random_number():
        """
        Función encargada de generar un numero random que no este en la tabla code_mail
        """
        random_numbers = str(random.randint(100000, 999999))
        if CodeMail.objects.filter(code=random_numbers, status=True).exists():
            return StandarClass.random_number()
        return random_numbers

    def generete_code():
        longitud = random.randint(8, 10)
        caracteres = string.ascii_letters + string.digits
        codigo = ''.join(random.choices(caracteres, k=longitud))
        if Users.objects.filter(code_referral = codigo).exists():
            return StandarClass.generete_code()
        return codigo
    
    def timer_sale(self,registration_date,hour):
        """
        Función encargada de generar el timepo del timer con la fecha de inicio y final.
        """
        date_now = str(datetime.datetime.now())
        date_now =date_now.split(".")
        date_now_ms = datetime.datetime.strptime(f"{date_now[0]}", "%Y-%m-%d %H:%M:%S")
        date_now_ms = date_now_ms.timestamp()*1000
        date_limit = datetime.datetime.strptime(f"{registration_date} {hour}", "%Y-%m-%d %H:%M:%S")
        date_limit_ms = date_limit.timestamp()*1000
        date_limit_ms = date_limit_ms+float(self)
        timer = date_limit_ms-date_now_ms
        timer = int(timer)
        return max(timer, 0)

    
class AuthenticationClass:
    
    _permissions = {"ok":False,"error":"permissions error","description":"please check the data and try again"}
    _recaptcha = {"ok":False, "error":"recaptcha fail"}
    _report = {"ok":False, "error": "report cannot be generated because there is no data on these dates"}    
    
    def autohorization(self):
        """
        Request encargada de validar si el token es valido en el dominio o si esta vencido para no dejarlo pasar, en caso de que sea valido se comprobara si el usuario esta en una empresa activa
        """
        try:
            if BlackListedToken.objects.filter(token = self['Authorization']).exists():
                if BlackListedToken.objects.filter(token = self['Authorization'], status = False).exists(): 
                    return {"ok":False, "error":"You have been logged in on another device"} 
                data = jwt.decode(self['Authorization'], settings.SECRET_KEY, algorithms=["HS256"]) 
                return {"ok":True,"data":Users.objects.get(id = data['id'])}
            return {"ok":False ,"error":"You have been logged in on another device"} 
        except jwt.ExpiredSignatureError: return {"ok":False, "error":"Token expired", "message":"Enter the application again to continue browsing"}
        except jwt.DecodeError: return {"ok":False, "error":"Invalid token", "message":"This token is not from our domain"}
        except Exception: return {"ok":False, "error":"token was not provided"}
        
    def recaptcha(self):
        """
        Request encargada de tomar la respuesta del recaptcha y la envía a Google para verificar.
        """
        conn = http.client.HTTPSConnection("www.google.com")
        conn.request("POST", f"https://www.google.com/recaptcha/api/siteverify?secret={settings.RECAPTCHA_KEY_PRIVATE}&response={self['Authorization']}")
        res = conn.getresponse()
        data = res.read()
        deco = str(data.decode("utf-8"))
        valid = json.loads(deco)
        return (valid['success'])
    
class ClassTokens():
    ''' La clase UpdateCustomerData inicializa variables para `token, correo electrónico, clientes y un nuevo
     token.`
     '''
     
    
    def __init__(self, token=None, email=None, user=None, token_new=None):
        
        self.token=token
        self.email=email
        self.user= user
        self.token_new= token_new
    
    def creaction_token(self):
        """
        Toma una cadena y devuelve una cadena
        :return: el seguimiento:
        """
        user = Users.objects.get(id=self.user)
        payload = {
            'id':user.pk,
            'email': user.email,
            'username':user.username,
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'nbf': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=-5),
        }
        token = jwt.encode(payload, settings.SECRET_KEY)
        code = None
        if int(user.type_user) != 1:
            code = f"{settings.URL_FRONT}auth/register/{user.code_referral}"
        data = {
                'user_id': user.pk,
                'type_user':user.type_user,
                'email': user.email,
                "username":user.username, 
                "code_referral":code,
                "language":user.language,
                "wallet":user.wallet,
                # "cant_ref":user.referral.all().count(),
                "token":token
                }
        
        if int(user.type_user) == 1:
            data['wallet_sp'] = user.wallet_sp
            
        BlackListedToken.objects.update_or_create(
        user_id=user.pk,
        defaults={
            "token": token,
            "status": True
        }
        )
        return data
    
    def black_validate_list(self):
        """
        Comprueba si el token está en la lista negra o no
        :return: Un valor booleano
        """
        """
        It checks if the token is blacklisted or not
        
        :param token: The token that you want to validate
        :return: A boolean value
        """
        if not (
            query_login := list(
                BlackListedToken.objects.filter(token=self.token).values(
                    'token', 'customers', 'status'
                )
            )
        ):
            return False
        res = json_convert(query_login)
        if res['status'] ==True:
            return True
        elif res['status'] ==False:
            return False
    
    def black_validate_update(self):
        """
        Comprueba si el token está en la lista negra o no
        :return: Se está devolviendo un diccionario con la clave "ok" y el valor True, y la clave
        "descripción" y el valor "solicitud exitosa"
        """
        """
        It checks if the token is blacklisted or not
        
        :param token: The token that you want to validate
        :return: A boolean value
        """
        BlackListedToken.objects.filter(token= self.token).update(user_id=self.user, token= self.token_new)
        return {"ok":True,"description":"resquest succes"}