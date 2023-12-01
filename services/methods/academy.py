from django.db import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.ServicesClass import AuthenticationClass
from services.connectionS3 import *
from services.serializers import *
from services.models import *
from rest_framework.parsers import JSONParser

@csrf_exempt
def get_type_document_get(request):
    if request.method != "GET":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)>=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 
    resource=[]
    data={1:"PDF",2:"DOC",3:"XLSX",4:"PPT",5:"Cursos",6:"Audio"}
    for i, j in list(Academy.choice_type_document):
        a={"id":i,"name":data[i]}
        resource.append(a)
    return JsonResponse({"ok":True,"data":resource})  
    

@csrf_exempt
def save_chapter(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 
    chapter=1
    if Series.objects.filter(academy=request.POST.get('id')).exists():
        get_chapters=Series.objects.filter(academy=request.POST.get('id')).last()
        chapter+=int(get_chapters.chapter)
    if "img" in request.FILES:
        url, new_name= StandarClass.upload_certification_file(request.FILES['img'])
    if "video" in request.FILES:
        url_video, new_name_video= StandarClass.upload_certification_file(request.FILES['video'])


    chapters=Series(title=request.POST.get('title'),img=url,key_img= new_name,description=request.POST.get('description'),chapter=chapter,url=url_video,key_url=new_name_video,academy_id=request.POST.get('id'))
    chapters.save()
    return JsonResponse({"ok":True,"data":"Save sucesfully"}, safe=False)

@csrf_exempt
def get_files_academy(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)>=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 
    query_resource = []
    Data=JSONParser().parse(request)
    if int(auth['data'].type_user)==2:
        if Data['language']!="all" and Data['type_document']!="docs":
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=Data['language'],type_document=Data['type_document']).order_by('-id'), many=True).data)
        elif Data['language']=="all" and Data['type_document']=="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(type_document__in=[1,2,3,4]).order_by('-id'), many=True).data)
        elif Data['language']=="all" and Data['type_document']!="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(type_document=Data['type_document']).order_by('-id'), many=True).data)
        elif Data['language']!="all" and Data['type_document']=="docs":
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=Data['language'],type_document__in=[1,2,3,4]).order_by('-id'), many=True).data)
    if int(auth['data'].type_user)!=2:
        #User
        if Data['type_document']=="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=auth['data'].language,type_document__in=[1,2,3,4]).order_by('-id'), many=True).data)
        elif Data['type_document']!="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=auth['data'].language,type_document=Data['type_document']).order_by('-id'), many=True).data)
        elif Data['type_document']!="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=auth['data'].language,type_document=Data['type_document']).order_by('-id'), many=True).data)
        elif Data['type_document']=="docs": 
            query_resource =  change_choices_files_academy(AcademySerializers(Academy.objects.filter(language=auth['data'].language,type_document__in=[1,2,3,4]).order_by('-id'), many=True).data)   
    return JsonResponse({"ok":True,"data":query_resource})


@csrf_exempt
def get_type_file(request):
    if request.method != "GET":return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)

    if int(auth['data'].type_user)>=4:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False) 
    resource=[];profile=[]
    data={1:"PDF",2:"DOC",3:"XLSX",4:"PPT",5:"Video",6:"Imagen"}
    choice_type_resource=(
        (1,'pdf'),
        (2,'doc'),
        (3,'xlsx'),
        (4,'ppt'),
        (5,'video'),
        (6, 'imagen')
    )   
    choice_type_profile=(
        (1,'Networker'),
        (2,'Universitarios'),
        (3,'Ambientalistas'),
        (4,'Empresarios')
    )
    for i, j in list(choice_type_resource):
        a={"id":i,"name":data[i]}
        resource.append(a)
    for i, j in list(choice_type_profile):
        a={"id":i,"name":j}
        profile.append(a)
    return JsonResponse({"ok":True,"data":{"types_resource":resource,
                                               "types_profile":profile}})   

def change_choices_files_academy(resp):
    data={1:"PDF",2:"DOC",3:"XLSX",4:"PPT",5:"Cursos",6:"Audio"}
    for index in resp:
        # index['created'] = index['created'].split("T")[0] 
        if int(index['type_document'])==5:
            index['count_chapters']=Series.objects.filter(academy=index['id']).count()
        
        if index['key_img'] != None:
            
            index['img'] = FilesS3(key=index['key_img']).refresh()
        if index['key_file'] != None:
            index['document'] = FilesS3(key=index['key_file']).refresh()
        index['type_document']=data[index['type_document']]
    return resp 


@csrf_exempt
def get_curses(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)>=4:return JsonResponse(AuthenticationClass._permissions, status=401, safe=False)
    Data=JSONParser().parse(request)    
    resp=Series.objects.filter(academy=Data['id']).order_by('chapter').values('id','description','title','key_img','img','url','key_url','created')
    for index in resp:
        if index['key_url'] != None:
            index['url'] = FilesS3(key=index['key_url']).refresh()
        if index['key_img'] != None: 
            index['img']=FilesS3(key=index['key_img']).refresh()
    return JsonResponse({"ok":True,"data":list(resp)}, status=200,safe=False)


@csrf_exempt
def edit_file_academy(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user) not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)

    if Academy.objects.filter(id=request.POST.get('id')).exists():
        if 'document' in request.FILES and request.POST.get('type_document')!=5:
            url_document, new_name_document = StandarClass.upload_certification_file(request.FILES['document'])
            Academy.objects.filter(id=request.POST.get('id')).update(document=url_document,key_file=new_name_document)
            
        if 'img' in request.FILES:
            
            url, new_name = StandarClass.upload_certification_file(request.FILES['img'])
            Academy.objects.filter(id=request.POST.get('id')).update(img=url,key_img=new_name)

            
        res=Academy.objects.filter(id=request.POST.get('id')).get()
        if request.POST.get('title')!='null':
            res.title=request.POST.get('title')
        if request.POST.get('language')!='null':
            res.language=request.POST.get('language')
        if request.POST.get('description')!='null':
            res.description=request.POST.get('description')
        if request.POST.get('time_audio')!='null':
            res.time_audio=request.POST.get('time_audio')
        if request.POST.get('author')!='null':
            res.author=request.POST.get('author')
        res.save()
    return JsonResponse({"ok":True,"data":"Update File"})

@csrf_exempt
def delete_academy(request):
    if request.method != 'DELETE':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    Data=JSONParser().parse(request)  
    if Academy.objects.filter(id=Data['id']).exists():
        res=Academy.objects.filter(id=Data['id']).get()
        list_files=[]
        if res.key_file!=None:
            list_files.append(res.key_file)
        if res.key_img!=None:
            list_files.append(res.key_img)
        if int(res.type_document)==5:
            if Series.objects.filter(academy=res.pk).exists():
                resp=Series.objects.filter(academy=res.pk).values('id','key_img','key_url')
                for index in resp:
                    if index['key_url']!= None:
                        list_files.append(index['key_url'])
                    if index['key_img']!=None:
                        list_files.append(index['key_img'])
                        Series.objects.filter(id=index['id']).delete()
        for index in list_files:
            FilesS3(key=index).delete_file()
        Academy.objects.filter(id=Data['id']).delete()
    return JsonResponse({"ok": True,"data":"Delete File"})

@csrf_exempt
def delete_course_video(request):
    if request.method != 'DELETE':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    Data=JSONParser().parse(request)  
    list_files=[]
    if Series.objects.filter(id=Data['id']).exists():
        resp=Series.objects.filter(id=Data['id']).get()
        if resp.key_img!=None:
            list_files.append(resp.key_img)
        if resp.key_url != None:
            list_files.append(resp.key_url)
        Series.objects.filter(id=Data['id']).delete()
    for index in list_files:
        FilesS3(key=index).delete_file()
    return JsonResponse({"ok": True,"data":"Delete video file"})

@csrf_exempt
def edit_course_video(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)
    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    if Series.objects.filter(id=request.POST.get('id')).exists():
        chapters=Series.objects.filter(id=request.POST.get('id')).get()
        if "img" in request.FILES:
            url, new_name= StandarClass.upload_certification_file(request.FILES['img']) 
            chapters.img= url
            chapters.key_img = new_name
            
        if "video" in request.FILES:
            url_video, new_name_video= StandarClass.upload_certification_file(request.FILES['video']) 
            chapters.url=url_video
            chapters.key_url = new_name_video
        chapters.title=request.POST.get('title')
        chapters.description=request.POST.get('description')
        chapters.save()
    return JsonResponse({"ok":True,"data":"Save sucesfully"}, safe=False)

@csrf_exempt
def get_only_one_file(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    Data=JSONParser().parse(request)    
    if Academy.objects.filter(id=Data['id']).exists():
        res=(AcademySerializers(Academy.objects.filter(id=Data['id']), many=True).data)[0]
        data={1:"PDF",2:"DOC",3:"XLSX",4:"PPT",5:"Cursos",6:"audio"}
        res['type_file']=data[res['type_document']]
        if res['key_img']!= None:
            res['img'] = FilesS3(key=res['key_img']).refresh()
        if res['key_file'] != None:
            res['document'] = FilesS3(key=res['key_file']).refresh()
        del res['key_img'], res['key_file']
    return JsonResponse({"ok":True,"data":res}, status=200,safe=False)

@csrf_exempt
def get_only_video(request):
    if request.method != 'POST':return JsonResponse({"ok":False,"error":f"type requests are not allowed {request.method}"}, status=404,safe=False)

    auth = AuthenticationClass.autohorization(request.headers)
    if auth['ok'] != True: 
        return JsonResponse(auth, status=401, safe=False)
    if int(auth['data'].type_user)not in [1,2]:return JsonResponse(AuthenticationClass._permissions,status=401, safe=False)
    Data=JSONParser().parse(request)    
    if Series.objects.filter(id=Data['id']).exists():
        resp=Series.objects.filter(id=Data['id']).values('id','description','url','img','title','key_img','key_url','created')[0]
        if resp['key_img'] != None:
            resp['img'] = FilesS3(key=resp['key_img']).refresh()
        if resp['key_url'] != None:
            resp['url'] = FilesS3(key=resp['key_url']).refresh()
    return JsonResponse({"ok":True,"data":resp}, status=200,safe=False)