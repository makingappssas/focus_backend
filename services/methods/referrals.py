from django.db import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from block_chain.models import Nft, NftHistory
from services.ServicesClass import AuthenticationClass
from services.connectionS3 import *
from services.serializers import *
from services.models import *
from rest_framework.parsers import JSONParser
from web3 import Web3

@csrf_exempt
def amount_ref(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": f"requests of type {request.method} are not allowed"}, status=404, safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    amount_ref = float(auth['data'].acumulated_ref)
    amount_ref = "{:.3f}".format(float(auth['data'].acumulated_ref)+float(auth['data'].acumulated_nft)).rstrip('0')
    if amount_ref.endswith('.'):
        amount_ref = amount_ref[:-1]
    return JsonResponse({"ok":True,"data":{"amount_ref":amount_ref, "nft_count":int(Nft.objects.using('db2').filter(focus_id = auth['data'].pk).count())}},status= 200, safe=False)

@csrf_exempt
def get_referrals(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": f"requests of type {request.method} are not allowed"}, status=404, safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) >= 4:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    data = JSONParser().parse(request)
    random_id = None
    type_nft = 0
    price = 0
    # history = None
    if data['type'] != None:
        random_nft = Nft.objects.using('db2').filter(owner_id=None, type_nft=data['type'], focus_id = None).exclude(owner__isnull=False).order_by('?').first()    
        if random_nft:
            random_id = random_nft.pk
            nft = Nft.objects.using('db2').get(id = random_nft.pk)
            type_nft = nft.type_nft
            price = nft.price
            # nft = Nft.objects.get(id = data['nft_id'])
            # history = NftHistory.objects.create(nft_id = data['nft_id'], type_nft = nft.type_nft, user_id = auth['data'].pk, nft_recieved=f"{nft.name}#{nft.pk}", status = False)
            # nft.owner = auth['data'].pk
            # nft.save()
    usuario = Users.objects.get(id=auth["data"].pk)
    lista_1 = [usuario.pk]
    user_principal = 0
    porcentajes = [15,5,4,3,5,1,2,3,1,1,5]
    wallet = []
    porcent = []
    count = 0
    while lista_1 and user_principal == 0:
        if len(wallet) == len(porcentajes):
            break
        new_list = []
        for user_id in lista_1:
            referral_ids = RelationRef.objects.filter(to_usuario_id=user_id).values_list('from_usuario_id', flat=True)
            if len(referral_ids) == 0:
                user_principal = user_id
                break
            new_list.extend(referral_ids)
        lista_1 = new_list
        if lista_1 != []:
            u=Users.objects.get(id__in=lista_1)
            if u.wallet != None:
                wallet.append(u.wallet)
                porcent.append(porcentajes[count])
        count += 1
        if count == 11:
            break
    
    
    sp = Users.objects.get(id = 1)
    # porcent.append(5)
    # wallet.append(sp.wallet)
    # return JsonResponse({"ok":True,"data":{"wallet":wallet, "porcent":porcent,"random_id":random_id, "price":price, "history_id":history}}, safe=False)
    return JsonResponse({"ok":True,"data":{"wallet":wallet, "porcent":porcent,"random_id":random_id, "type_nft":type_nft,"price":price, "wallet_sp":sp.wallet_sp, "token_uri":f"{settings.URL_FRONT}/api/TokenId/{random_id}"}}, safe=False)


@csrf_exempt
def wallet_sp(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": f"requests of type {request.method} are not allowed"}, status=404, safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    
    if int(auth['data'].type_user) != 1:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    data=JSONParser().parse(request)  
    try:
        if auth['data'].wallet_sp == None:
            is_valid = Web3().is_address(data['wallet'])
            # Imprimir el resultado de validación
            if not is_valid and data['wallet'] != None:
                return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
            auth['data'].wallet_sp = data['wallet']
            auth['data'].save()
        else:
            if not CodeMail.objects.filter(code = data['code']).exists():
                return JsonResponse({"ok":False,"error":"código incorrecto"}, status= 403, safe=False)
            if not CodeMail.objects.filter(user_mail = auth['data'].email, status=True).exists():
                return JsonResponse({"ok":False,"error":"Este código ya expiro o fue usado, solicita otro."}, status= 403, safe=False)
            
            CodeMail.objects.filter(user_mail = auth['data'].email).update(status=False)
            is_valid = Web3().is_address(data['wallet'])
            # Imprimir el resultado de validación
            if not is_valid and data['wallet'] != None:
                return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
            auth['data'].wallet_sp = data['wallet']
            auth['data'].save()
        return JsonResponse({"ok":True,"data":"update sucess"}, safe=False)
    except:
        return JsonResponse({"ok":False,"error":"This address already in other account"},status= 403)
    
@csrf_exempt
def post_wallet(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": f"requests of type {request.method} are not allowed"}, status=404, safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    
    if int(auth['data'].type_user) >= 4:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    data=JSONParser().parse(request)  
    
    if data['wallet'] == None:
            return JsonResponse({"ok":False,"error":"This address already in other account"}, status= 403)
    elif data['wallet'] != None: 
        if Users.objects.filter(wallet = data['wallet']).exists():
            return JsonResponse({"ok":False,"error":"This address already in other account"}, status= 403)
    try:
        if auth['data'].wallet == None:
            is_valid = Web3().is_address(data['wallet'])
            # Imprimir el resultado de validación
            if not is_valid and data['wallet'] != None:
                return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
            auth['data'].wallet = data['wallet']
            auth['data'].save()
        else:
            if not CodeMail.objects.filter(code = data['code']).exists():
                return JsonResponse({"ok":False,"error":"código incorrecto"}, status= 403, safe=False)
            if not CodeMail.objects.filter(user_mail = auth['data'].email, status=True).exists():
                return JsonResponse({"ok":False,"error":"Este código ya expiro o fue usado, solicita otro."}, status= 403, safe=False)
            
            CodeMail.objects.filter(user_mail = auth['data'].email).update(status=False)
            is_valid = Web3().is_address(data['wallet'])
            # Imprimir el resultado de validación
            if not is_valid and data['wallet'] != None:
                return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
            auth['data'].wallet = data['wallet']
            auth['data'].save()
        return JsonResponse({"ok":True,"data":"update sucess"}, safe=False)
    except:
        return JsonResponse({"ok":False,"error":"This address already in other account"},status= 403)


@csrf_exempt
def post_wallet_connection(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": f"requests of type {request.method} are not allowed"}, status=404, safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    
    if int(auth['data'].type_user) >= 4:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)    
    data=JSONParser().parse(request)  
    is_valid = Web3().is_address(data['wallet'])
    # Imprimir el resultado de validación
    if not is_valid and data['wallet'] != None:
        return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
    auth['data'].connection = data['wallet']
    auth['data'].save()
    return JsonResponse({"ok":True,"data":"update sucess"}, safe=False)

@csrf_exempt
def get_referrals_list(request):
    if request.method!="POST":
        return JsonResponse({"ok":False,"error":"Only allowed method POST"}, status=403,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    data = JSONParser().parse(request)
    if int(auth['data'].type_user) >= 4:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    if data['id'] == 0 and int(auth['data'].type_user) == 3 :
        user = list(Users.objects.filter(id=auth['data'].pk, referral__id__isnull=False).order_by('-id').values('referral__id','referral__username'))
        username = auth['data'].username
    elif data['id'] == 0 and int(auth['data'].type_user) == 2 :
        user = []
        for index in list(Users.objects.filter( invitation_id= None).exclude(type_user__in=[1,2]).values('id','username')):
            index['referral__id'] = index['id']
            index['referral__username'] = index['username']
            del index['id'], index['username']
            user.append(index)
        username = auth['data'].username    
    else:
        user = list(
            Users.objects
            .filter(id=data['id'])
            .exclude(referral__id__isnull=True)
            .exclude(referral__isnull=True, type_user__in=[1,2])
            .order_by('-id')
            .values('referral__id', 'referral__username')
        )
        username = Users.objects.get(id=data['id']).username
    
    return JsonResponse({"ok": True,"data": {"user": username, "resp": user}})

@csrf_exempt
def get_users_cant(request):
    if request.method!="GET":
            return JsonResponse({"ok":False,"error":"Only allowed method GET"}, status=403,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) != 2:
        return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    return JsonResponse({"ok": True,"data": Users.objects.all().exclude(type_user__in=[1,2]).count()})

