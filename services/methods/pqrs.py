from django.views.decorators.csrf import csrf_exempt
from services.ServicesClass import AuthenticationClass
from services.connectionS3 import FilesS3
from services.connectionS3 import StandarClass
from services.translations.en import en
from services.translations.es import es
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from services.models import Users, Notifications, Users, Pqrs, Messages, Users
from services.serializers import PqrsListSerializers


@csrf_exempt
def ListCategory(request):
    """ 
    Request encargada de mandar la lista de categorias de pqrs de la base de datos
    """
    if request.method=='GET':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)        
        response=[]
        for i, j in list(Pqrs.choices_category):
            response.append({"id_category":i, "name_pqrs_category":j})
        return JsonResponse(response, status=200, safe=False)


@csrf_exempt
def ListStatus(request):
    """
    Request encargada de mandar la lista de los estados de las pqrs de la base de datos
    """
    if request.method=='GET':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        response = []
        for i, j in list(Pqrs.choices_status):
            response.append({"id_status":i, "name_pqrs_status":j})
        return JsonResponse(response, status=200, safe=False)


@csrf_exempt
def CreateTicket(request):
    """
    Request encargada de mandar la lista de los estados de las pqrs de la base de datos
    """
    if request.method=='POST':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        Data = JSONParser().parse(request)
        pqrs_data = Pqrs.objects.create(
            user_id=auth['data'].pk,
            name_pqrs=Data['name_pqrs'],
            category=Data['category'],
            status=1)  
        return JsonResponse({"ok":"resquest succes", "description":"create tickets", "id_tickets":pqrs_data.pk}, status=201, safe=False)
               

@csrf_exempt
def FinishedTickets(request):  
    """
    Request encargada de finalizar uan las pqrs desde el rol superadmin
    """
    if request.method=='PUT':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        Data = JSONParser().parse(request)
        Pqrs.objects.filter(id = Data['id']).update(status = 3)
        return JsonResponse({"ok":"resquest succes", "description":"Updated data"}, status=201, safe=False)


@csrf_exempt
def Chat(request):
    """
    Request encargada de entregar todos los mensajes de un chat
    """
    if request.method=='POST':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        Data = JSONParser().parse(request)
        messages = list(Messages.objects.filter(pqrs_id = Data["id"]).values('id','pqrs_id', 'author','contents','img','img_key').order_by('timestamp'))
        respones_menssages = []
        for message in messages:
            if message['img_key'] != None:
                message['img'] = FilesS3(key = message['img_key']).refresh()
                Messages.objects.filter(id = message["id"]).update(img = message['img'])
            del message['id']
            respones_menssages.append(message)
        pqrs = Pqrs.objects.filter(id=Data['id']).get()
        return JsonResponse({'status_pqrs':pqrs.status,'name_chat':pqrs.name_pqrs,'message':respones_menssages}, safe=False, status=200)


@csrf_exempt
def TicketsFilter(request):
    """
    Request encargada de enlistar todas las solicitudes de pqrs de la plataforma
    """
    if request.method=='POST':

        auth = AuthenticationClass.autohorization(request.headers)
        if auth['ok'] != True: 
            return JsonResponse(auth, status=401, safe=False)
        Data = JSONParser().parse(request)
        if int(auth['data'].type_user)==2:
            if (Data['category']==0 and Data['status']==0):
                pqrs_data = Pqrs.objects.all().exclude(status=3).order_by('id')                            
            elif (Data['category']!=0 and Data['status']==0):
                pqrs_data = Pqrs.objects.filter(category=Data['category']).order_by('id')           
            elif (Data['category']==0 and Data['status']!=0):
                pqrs_data = Pqrs.objects.filter(status=Data['status']).order_by('id')
            elif (Data['category']!=0 and Data['status']!=0):
                pqrs_data = Pqrs.objects.filter(status=Data['status'],category=Data['category']).order_by('id')
        else:
            if (Data['category']==0 and Data['status']==0):
                pqrs_data = Pqrs.objects.filter(user_id = auth['data'].pk).exclude(status=3).order_by('id')                           
            elif (Data['category']!=0 and Data['status']==0):
                pqrs_data = Pqrs.objects.filter(category=Data['category'],user_id = auth['data'].pk).order_by('id')         
            elif (Data['category']==0 and Data['status']!=0):
                pqrs_data = Pqrs.objects.filter(status=Data['status'],user_id = auth['data'].pk).order_by('id')
            elif (Data['category']!=0 and Data['status']!=0):
                pqrs_data = Pqrs.objects.filter(status=Data['status'],category=Data['category'],user_id=auth['data'].pk).order_by('id')
        response = []
        pqrs_serializer=PqrsListSerializers(pqrs_data,many=True)
        if len(pqrs_serializer.data) == 0:
            return JsonResponse(response, status=200, safe=False)
        else:
            for index in pqrs_serializer.data:
                person = Users.objects.get(id=index['user_id'])
                category = dict(Pqrs.choices_category)[index['category']]
                status = dict(Pqrs.choices_status)[index['status']]
                if int(auth['data'].type_user )== 1:
                    index['status_noti'] = index['status_noti']
                elif index['status_noti'] == False and int(auth['data'].type_user )!=2:
                    index['status_noti'] = True
                else:
                    index['status_noti'] = False              
                tickets={
                    'id': index['id'],
                    'status_noti': index['status_noti'],
                    'name_pqrs': index['name_pqrs'],
                    'category': category,
                    'status': status,
                    'name': person.username,
                    }
                response.append(tickets)
        return JsonResponse(response[::-1],status=200,safe=False)