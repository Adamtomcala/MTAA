import django.core.exceptions
import datetime
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from . import models
# Create your views here.

file_extensions = ['.pdf', '.txt']


# Asi hotovo
def login(request, username, password):
    if request.method == 'GET':
        try:
            # Najdenie pouzivatela
            user = models.User.objects.get(user_name=username, password=password)

            u = user.user_type_id

            # Filtrovanie sprav na zaklade user.id
            messages = models.Message.objects.filter(receiver_id=user.id)
            count = messages.count() if messages.count() < 3 else 2

            msgs = []
            # Iterovanie cez spravy
            for i in range(count):
                receiver = models.User.objects.get(id=messages[i].sender_id)
                msg = {
                    'message_sender': receiver.first_name + ' ' + receiver.last_name,
                    'message_name': messages[i].name,
                    'created_at': messages[i].created_at,
                }
                msgs.append(msg)

            # V spojovacej tabulke najdenie vsetkych pouzivatelov s prislusnym user id
            records = models.ClassroomUser.objects.filter(user_id=user.id)

            classrooms_ids = []
            # Zistenie vsetkych classroom id, kde sa nachadza pouzivatel
            for record in records:
                classrooms_ids.append(record.classroom.id)


            materials = []
            owners = {}
            # Iterovanie cez jednotlive triedy a hladanie materialov a vlastnikov classroom-ov
            for ci in classrooms_ids:
                materials.append(models.Material.objects.filter(classroom_id=ci))
                users = models.ClassroomUser.objects.filter(classroom=ci)
                for u in users:
                    # predpokladam, ze iba jeden ucitel bude mat triedu
                    if u.user.user_type_id.id == 1:
                        owners[ci] = u
                        break

            mtrs = []
            # iterovanie cez materialy jednotlivych tried
            for material in materials:
                for m in material:
                    receiver = owners[m.classroom_id.id]
                    mtr = {
                        'material_sender': receiver.user.first_name + ' ' + receiver.user.last_name,
                        'material_name': m.name,
                        'created_at': m.created_at,
                    }
                    mtrs.append(mtr)

            # vytvorenie vysledku
            result = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_name': user.user_name,
                'user_type_id': u.id,
                'messages': msgs,
                'materials': mtrs[:2],
            }

            return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})
        # Tento except hovori, ze dany objekt neexistuje (bud chybne heslo alebo meno)
        except django.core.exceptions.ObjectDoesNotExist:
            try:
                # Vyhladanie pouzivatela, so zadanym pouzivatelskym menom
                models.User.objects.get(user_name=username)

                result = {
                    'status': 'Zle heslo',
                }

                return JsonResponse(result, safe=False, status=401, json_dumps_params={'indent': 3})
            except django.core.exceptions.ObjectDoesNotExist:
                result = {
                    'status': 'Nespravne meno',
                }

                return JsonResponse(result, safe=False, status=401, json_dumps_params={'indent': 3})


# Asi hotovo
def get_messages(request):
    # Tato funkcia sluzi na spracovanie requestov pre zobrazenie sprav pouzivatela na obrazovke SPRAV
    if request.method == 'GET':
        params = request.GET.dict()
        # Nastavenie rozsahu sprav
        fromm, to = (int(params['page']) - 1) * 5,  (int(params['page'])) * 5

        messages = models.Message.objects.filter(receiver_id=int(params['id']))[fromm:to]

        # Ak pouzivatel nema ziadne spravy
        if len(messages) == 0:
            result = {
                'status': 'Ziadne spravy'
            }
            return JsonResponse(result, status=200, safe=True)

        result = {}
        mess = []
        for m in messages:
            msg = {
                'name': m.name,
                'sender': m.sender.first_name + ' ' + m.sender.last_name,
                'text': m.text,
                'created_at': m.created_at,
            }
            mess.append(msg)
        result['messages'] = mess

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})


# Asi hotovo
@csrf_exempt
def password(request, username, password):
    # Funkcia sluzi na spracovanie GET/PUT requestov pri zmene hesla pouzivatela

    # Tento GET request sluzi na odoslanie overenia zadaneho stareho hesla
    if request.method == 'GET':
        try:
            user = models.User.objects.get(user_name=username, password=password)
            result = {
                'status': 'Spravne heslo',
            }
            return JsonResponse(result, safe=False, status=200, json_dumps_params={'indent': 3})
        except django.core.exceptions.ObjectDoesNotExist:
            result = {
                'status': 'Zle heslo',
            }
            return JsonResponse(result, status=400, safe=False, json_dumps_params={'indent': 3})

    # Tento PUT request sluzi pre aktualizovanie stareho pouzivatela na nove
    elif request.method == 'PUT':
        user = models.User.objects.get(user_name=username)

        # Ak sa stare anove heslo bude zhodovat
        if password == user.password:
            result = {
                'status': 'Hesla sa zhoduju',
            }
            return JsonResponse(result, status=403, safe=False, json_dumps_params={'indent': 3})

        user.password = password
        user.save()
        result = {
            'status': 'Heslo zmenene',
        }
        return JsonResponse(result, status=201, safe=False, json_dumps_params={'indent': 3})


# Asi hotovc
def find_user(request, username):
    # Tato funkcia spracuvava GET requesty pri vyhladani pouzivatelov na volanie
    if request.method == 'GET':
        try:
            users = models.User.objects.filter(user_name__icontains=username)[:3]
            result = {}
            names = []

            for user in users:
                names.append(user.first_name + ' ' + user.last_name)
            result['users'] = names

            return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})

        except django.core.exceptions.ObjectDoesNotExist:
            result = {
                'status': 'Pouzivatel neexistuje',
            }
            return JsonResponse(result, status=400, safe=False, json_dumps_params={'indent': 3})


# Asi hotovo
@csrf_exempt
def upload_file(request, user_id):
    # Funkcia sluzi na spracovanie GET/POST/DELETE requestu
    # Kvoli akceptacnym testom, bude tam nejaky button, ktory zavola tento predment,
    # Ak bude pouzivatel student vyskoci hlaska o nepovolenie
    # Ak bude pouzivatel ucitel, tak hlaska o potvrdenie pridania/vymazanie materialu

    # Tento GET request je na to overovanie
    if request.method == 'GET':
        user = models.User.objects.get(id=user_id)
        result = {}

        # Ak sa o to pokusi student
        if user.user_type_id.id != 1:
            result['status'] = 'Nepovolene'
            return JsonResponse(result, status=401, safe=False, json_dumps_params={'indent': 3})

        result['status'] = 'Povolene'
        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})

    # Tento POST na upload suboru
    elif request.method == 'POST':
        file_name = request.FILES['file']
        params = request.POST.dict()

        # Ak pridavany subor bude mat nepovolenu koncovku -> chyba
        if str(file_name) in file_extensions:
            result = {
                'status': 'Problem pri pridavani suboru.'
            }
            return JsonResponse(result, status=400, safe=False)

        path = default_storage.save('materials/' + str(file_name), ContentFile(file_name.read()))

        user = models.User.objects.get(id=user_id)

        classroom = models.Classroom.objects.get(id=int(params['classroom_id']))

        now = datetime.datetime.now()

        new_material = models.Material.objects.create(classroom_id=classroom,
                                                      name=params['name'], path=path,
                                                      created_at=now)
        new_material.save()
        result = {
            'id': new_material.id,
            'created_at': new_material.created_at,
            'teacher': user.first_name + ' ' + user.last_name,
        }

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})

    # Tento Delete sluzi na odstranenie materialu z classroomy
    elif request.method == 'DELETE':
        body = json.loads(request.body.decode('utf-8'))
        material = models.Material.objects.get(id=body['material_id'])

        result = {
            'material_name': material.name,
        }

        os.remove(material.path)
        material.delete()

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})
