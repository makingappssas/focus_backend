from django.db import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.ServicesClass import AuthenticationClass
from services.serializers import *
from services.models import *
from rest_framework.parsers import JSONParser

@csrf_exempt
def notification(request):
    if request.method != "POST":
        return
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) not in [1,2]:return JsonResponse({"ok":False,"error":"You don't have permissions to do this"}, status=401, safe=False)
    Data = JSONParser().parse(request)
    if Data['ids'] in ["es", "en"]:
        json={"es":"es",
              "en":"en"}
        query=list(Users.objects.filter(language=json[Data['ids']]).exclude(type_user__in=[1,2]).values())
    else:
        query=list(Users.objects.filter(id__in=Data['ids']).values())
    list_bulk=creation_notification(Data, query)
    Notifications.objects.bulk_create(list_bulk)
    return JsonResponse({"ok":True,"data":"Notifications created"})

def creation_notification(Data, query):
    return [
        Notifications(
            status='No leido',
            subject=Data['subject'],
            text_notification=Data['description'],
            url=Data['url'],
            status_icon=Data['status_icon'],
            user_id=index['id'],
        )
        for index in query
    ]

@csrf_exempt
def notification_get(request):
    if request.method=="GET":
        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
    resp = NotificationSerlializers(Notifications.objects.filter(user_id=auth['data'].pk).order_by('-id'), many=True).data
    for index in resp:
        Notifications.objects.filter(id=index['id']).update(status='Leido')
    return JsonResponse({"ok":True,"data":resp})
       
  
@csrf_exempt 
def cant_notications(request):
    """
    It returns the number of notifications that have not been read by the user
    
    :param request: The request object
    :return: the number of notifications that have not been read
    """
    # Una función que devuelve el número de notificaciones que no han sido leídas por el usuario
    if request.method=='GET': 
        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        count={"CantNotif":Notifications.objects.filter(user_id=auth['data'].pk,status='No leido').count()}
        return JsonResponse({"ok":True,"data":count},status=200,safe=False)

@csrf_exempt
def notification_delete(request):
    """
    A function that receives a request of type DELETE, validates the token, and if it is valid, it
    deletes the notifications that are in the list of notifications that are in the body of the request
    
    :param request: The request object
    :return: the notifications of the user
    """
    # Una función que recibe una solicitud de tipo DELETE, valida el token y, si es válido, elimina
    # las notificaciones que están en la lista de notificaciones que están en el cuerpo de la
    # solicitud.
    if request.method != 'DELETE':
        return
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    Data=JSONParser().parse(request)
    resp=NotificationSerlializers(Notifications.objects.filter(id__in=Data['id_notification']), many=True).data
    response="Notification delete"
    if len(resp)>1:
        response="Notifications were removed"
    for index in resp:
        Notifications.objects.filter(id=index['id']).delete()
    return JsonResponse({"ok":True,"data":response},status=201)