from django.db import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from block_chain.models import *
from services.ServicesClass import AuthenticationClass
from services.connectionS3 import *
from services.models import *
from rest_framework.parsers import JSONParser
from ..json_nft import NFT

@csrf_exempt
def get_token_id(request, param):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": f"Type requests are not allowed {request.method}"}, status=404, safe=False)
    try:
        nft = Nft.objects.using('db2').get(id=int(param))
        json = NFT[int(nft.type_nft)]
        json['name'] = f"{json['name'].split('#')[0]}#{nft.pk}"
        return JsonResponse(json)
    except:
        return JsonResponse({"ok": False, "error": "The provided ID is incorrect and does not match any NFT."}, status=403, safe=False)

@csrf_exempt
def get_cant_allow_nft(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": f"Type requests are not allowed {request.method}"}, status=404, safe=False)
    
    auth = AuthenticationClass.autohorization(request.headers)
    if not auth['ok']:
        return JsonResponse(auth, status=401, safe=False)
    return JsonResponse({"ok": True, "data":{"Classic":Nft.objects.using('db2').filter(type_nft = 1, owner_id = None, focus_id = None).count(),"Elite":Nft.objects.using('db2').filter(type_nft = 2, owner = None, focus_id = None).count(),"Royal":Nft.objects.using('db2').filter(type_nft = 3, owner = None,focus_id = None).count()}}, status=200, safe=False)

@csrf_exempt
def get_nft(request):
    if request.method != "GET":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    resp =list(Nft.objects.using('db2').filter(owner = None, focus_id = None).values('id','name','price','date_creation'))
    for index in resp:
        index['name'] = f"{index['name']}-{index['id']}"
    return JsonResponse({"ok":True,"data":resp})

@csrf_exempt
def get_my_nfts(request):
    if request.method != "GET":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    resp =list(Nft.objects.using('db2').filter(focus_id = auth['data'].pk, owner_id = None).values('id','name','type_nft','price','date_creation', 'focus_id'))
    for index in resp:
        index['name'] = f"{index['name']}#{index['id']}"
        index['img'] = NFT[int(index['type_nft'])]['image']
    return JsonResponse({"ok":True,"data":resp})

@csrf_exempt
def buy_nft(request):
    if request.method != "POST":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    data = JSONParser().parse(request)
    if data['status'] == True:
        count = 0
        nft = Nft.objects.using('db2').get(id = data['nft_id'])
        for index in data['porcent']:
            get = Users.objects.get(wallet = data['wallet'][count])
            porcen = ((index/100)*float(data['amount_send_usdt']))
            suma  = porcen +float(get.acumulated_nft)
            Users.objects.filter(id = get.pk).update(acumulated_nft = suma)
            Historic.objects.create(
                                    hash_transaction = data['hash_transaction'], 
                                    amount_send_usdt = (index/100)*float(data['amount_send_usdt']),
                                    address_send = data['wallet'][count], 
                                    username_from = auth['data'].username,
                                    user_id = get.pk)
            count +=1
        Nft.objects.using('db2').filter(id=data['nft_id']).update(focus_id = auth['data'].pk)
        nft = Nft.objects.using('db2').get(id = data['nft_id'])
        data['type_nft'] = nft.type_nft
        data['nft_recieved'] = f"{nft.name}#{nft.pk}"
        data['user_id'] = auth['data'].pk
    del data['wallet'], data['porcent'], data['nft_id']
    NftHistory.objects.create(**data)
    return JsonResponse({"ok":True,"data":"transaction complete"})

@csrf_exempt
def history_nft(request):    # sourcery skip: low-code-quality, merge-else-if-into-elif, remove-redundant-if
    if request.method != "POST":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) >=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    data = JSONParser().parse(request)
    amount_usdt = 0; classic =0; elite =0; royal=0
    if int(auth['data'].type_user) == 2:
        for index in list(NftHistory.objects.filter(type_nft = 1).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')):
            amount_usdt+=float(index['amount_send_usdt'])
            classic+=1
            
        for index in list(NftHistory.objects.filter(type_nft = 2).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')):
            amount_usdt+=float(index['amount_send_usdt'])
            elite+=1
            
        for index in list(NftHistory.objects.filter(type_nft = 3).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')):
            amount_usdt+=float(index['amount_send_usdt'])
            royal+=1
        
        amount_usdt = "{:.3f}".format(float(amount_usdt)).rstrip('0')
        if amount_usdt.endswith('.'):
            amount_usdt = amount_usdt[:-1]
            
        if data['date_start'] == "":
            
            if data['user'] == "" and data['status'] == "" and data['type_nft'] == "":
                lista_history = name_users(list(NftHistory.objects.all().values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
            elif data['user'] != "" and data['status'] == "" and data['type_nft'] == "":
                lista_history = name_users(list(NftHistory.objects.filter(user_id = data['id'],).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
            elif data['user'] != "" and data['status'] == "" and data['type_nft'] != "":
                lista_history = name_users(list(NftHistory.objects.filter(user_id = data['id'], type_nft = data['type_nft']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
            elif data['user'] == "" and data['status'] != "" and data['type_nft'] != "":
                lista_history = name_users(list(NftHistory.objects.filter(status = data['status'], type_nft = data['type_nft']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
            elif data['user'] == "" and data['status'] != "" and data['type_nft'] == "":
                lista_history = name_users(list(NftHistory.objects.filter(status = data['status']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
            elif data['user'] != "" and data['status'] != "" and data['type_nft'] != "":
                    lista_history = name_users(list(NftHistory.objects.filter(user_id = data['id'], status = data['status'], type_nft = data['type_nft']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            
        else:
            if data['date_end']=="":
                date = data['date_start'].split("T")
                lista_history = name_users(list(NftHistory.objects.filter(date_creation = date[0]).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(NftHistory.objects.filter(date_creation__gte = start[0], date_creation__lte = end[0]).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
    elif int(auth['data'].type_user) == 3:
        if data['date_start'] == "":
            if  data['status'] == "" and data['type_nft'] == "":
                lista_history = list(NftHistory.objects.filter(user_id = auth['data'].pk).values('id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id'))

            elif data['status'] !="" and data['type_nft'] == "":
                lista_history = list(NftHistory.objects.filter(user_id = auth['data'].pk, status = data['status']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id'))
            elif data['status'] !="" and data['type_nft'] != "":
                lista_history = list(NftHistory.objects.filter(user_id = auth['data'].pk, status = data['status'], type_nft = data['type_nft']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id'))
            
            elif data['status'] =="" and data['type_nft'] != "":
                lista_history = list(NftHistory.objects.filter(user_id = auth['data'].pk, type_nft = data['type_nft']).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id'))
        
        else:
            if data['date_end'] =="":
                start = data['date_start'].split("T")
                lista_history = name_users(list(NftHistory.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0]).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(NftHistory.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0], date_creation__lte = end[0]).values('user_id','id','hash_transaction','amount_send_usdt','nft_recieved','address_send','status','date_creation').order_by('-id')))
    return JsonResponse ({"ok":True,"data":{"history":lista_history, "cant_classic":classic,"cant_elite":elite,"cant_royal":royal, "amount_usdt":amount_usdt}},status = 200, safe=False)


@csrf_exempt
def history_ref(request):    # sourcery skip: low-code-quality, merge-else-if-into-elif, remove-redundant-if
    if request.method != "POST":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) >=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    data = JSONParser().parse(request)
    amount_usdt= 0
    if int(auth['data'].type_user) == 2:
        for index in Historic.objects.all().values().order_by('-id').exclude(user_id = 1):
            amount_usdt+=float(index['amount_send_usdt'])
        
        amount_usdt = "{:.3f}".format(float(amount_usdt)).rstrip('0')
        if amount_usdt.endswith('.'):
            amount_usdt = amount_usdt[:-1]
        if data['date_start'] == "":
            
            if data['user'] == "":
                lista_history = name_users(list(Historic.objects.all().values().order_by('-id').exclude(user_id = 1)))

            elif data['user'] != "" :
                lista_history = name_users(list(Historic.objects.filter(user_id = data['id'],).values().order_by('-id').exclude(user_id = 1)))

        else:
            if data['date_end']=="":
                date = data['date_start'].split("T")
                lista_history = name_users(list(Historic.objects.filter(date_creation = date[0]).values().order_by('-id').exclude(user_id = 1)))

            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(Historic.objects.filter(date_creation__gte = start[0], date_creation__lte = end[0]).values().order_by('-id').exclude(user_id = 1)))

    elif int(auth['data'].type_user) == 3:
        if data['date_start'] == "":
            lista_history = name_users(list(Historic.objects.filter(user_id = auth['data'].pk).values().order_by('-id').exclude(user_id = 1)))
        else:
            if data['date_end'] =="":
                start = data['date_start'].split("T")
                lista_history = name_users(list(Historic.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0]).values().order_by('-id').exclude(user_id = 1)))

            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(Historic.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0], date_creation__lte = end[0]).values().order_by('-id').exclude(user_id = 1)))

    return JsonResponse ({"ok":True,"data":{"history":lista_history,"amount_usdt":amount_usdt}},status = 200, safe=False)

def name_users(lista_history):
    for index in lista_history:
        index['user'] = Users.objects.get(id = index['user_id']).username
        amount_ref = "{:.3f}".format(float(index['amount_send_usdt'])).rstrip('0')
        if amount_ref.endswith('.'):
            amount_ref = amount_ref[:-1]
        index['amount_send_usdt'] = amount_ref
    return lista_history
            
            