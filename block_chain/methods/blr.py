from django.db import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from block_chain.models import BlrHistory, Historic
from services.ServicesClass import AuthenticationClass
from services.connectionS3 import *
from services.models import *
from rest_framework.parsers import JSONParser

@csrf_exempt
def buy_blr(request):
    if request.method != "POST":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    data = JSONParser().parse(request)
    data['user_id'] = auth['data'].pk
    # is_valid = Web3().is_address(data['address_send'])
    # # Imprimir el resultado de validación
    # if not is_valid and data['wallet'] != None:
    #     return JsonResponse({"ok":False,"error":"this address not valid"},status=403, safe=False)
    wallet, porcent = data['wallet'], data['porcent']
    if data['status'] == True:
        count = 0
        for index in porcent:
            get = Users.objects.get(wallet = wallet[count])
            get.acumulated_ref += (index/100)*float(data['amount_send_usdt'])
            get.save()
            Historic.objects.create(
                                    hash_transaction = data['hash_transaction'], 
                                    amount_send_usdt = (index/100)*float(data['amount_send_usdt']),
                                    address_send = wallet[count], 
                                    username_from = auth['data'].username,
                                    user_id = get.pk)
            count +=1
                
    
    del data['wallet'], data['porcent']
    BlrHistory.objects.create(**data)
    return JsonResponse({"ok":True,"data":"transaction created"})  

@csrf_exempt
def history_blr(request):  # sourcery skip: remove-redundant-if
    if request.method != "POST":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) >=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 

    data = JSONParser().parse(request)
    amount_usdt =0
    amount_blr =0
    if int(auth['data'].type_user) == 2:
        for index in BlrHistory.objects.all().values().order_by('-id').exclude(user_id = 1):
            amount_usdt += float(index['amount_send_usdt'])
            amount_blr += float(index['amount_recieved_blr'])
        amount_usdt = "{:.3f}".format(float(amount_usdt)).rstrip('0')
        if amount_usdt.endswith('.'):
            amount_usdt = amount_usdt[:-1]
        if data['date_start'] == "":
            if data['user'] == "" and data['status'] == "":
                lista_history = name_users(list(BlrHistory.objects.all().values()))
            elif data['user'] != "" and data['status'] == "":
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = data['id']).values().order_by('-id').exclude(user_id = 1)))
            elif data['user'] == "" and data['status'] != "":
                lista_history = name_users(list(BlrHistory.objects.filter(status = data['status']).values().order_by('-id').exclude(user_id = 1)))
        else:
            if data['date_end']=="":
                date = data['date_start'].split("T")
                lista_history = name_users(list(BlrHistory.objects.filter(date_creation = date[0]).values().order_by('-id').exclude(user_id = 1)))
            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(BlrHistory.objects.filter(date_creation__gte = start[0], date_creation__lte = end[0]).order_by('-id').values().exclude(user_id = 1)))
    elif int(auth['data'].type_user) == 3:
        if data['date_start'] == "":
            if  data['status'] == "":
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = auth['data'].pk).values().exclude(user_id = 1)))
            elif data['status'] != "":
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = auth['data'].pk, status = data['status']).values().order_by('-id').exclude(user_id = 1)))
            else:
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = auth['data'].pk, status = data['status']).values().order_by('-id').exclude(user_id = 1)))
        else:
            if data['date_end'] =="":
                start = data['date_start'].split("T")
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0]).values().order_by('-id').exclude(user_id = 1)))
            else:
                start = data['date_start'].split("T")
                end = data['date_end'].split("T")
                lista_history = name_users(list(BlrHistory.objects.filter(user_id = auth['data'].pk, date_creation__gte = start[0], date_creation__lte = end[0]).values().order_by('-id').exclude(user_id = 1)))
    return JsonResponse ({"ok":True,"data":{"history":lista_history, "acumulated_usdt":amount_usdt, "acumulated_blr":amount_blr}},status = 200, safe=False)

def name_users(lista_history):
    for index in lista_history:
        index['user'] = Users.objects.get(id = index['user_id']).username
        del index['user_id']
    return lista_history

            
            