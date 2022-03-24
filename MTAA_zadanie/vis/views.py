import django.core.exceptions
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from . import models
# Create your views here.


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

            print(classrooms_ids)

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
        except django.core.exceptions.ObjectDoesNotExist:
            try:
                user = models.User.objects.get(user_name=username)

                result = {
                    'message_error': 'Zle heslo',
                }

                return JsonResponse(result, safe=False, status=401, json_dumps_params={'indent': 3})
            except django.core.exceptions.ObjectDoesNotExist:#
                result = {
                    'message_error': 'Nespravne meno',
                }

                return JsonResponse(result, safe=False, status=401, json_dumps_params={'indent': 3})


def get_messages(request):
    if request.method == 'GET':
        params = request.GET.dict()
        fromm, to = (int(params['page']) - 1) * 5,  (int(params['page'])) * 5

        messages = models.Message.objects.filter(receiver_id=int(params['id']))[fromm:to]

        if len(messages) == 0:
            result = {
                'status': 'Ziadne spravy'
            }
            return JsonResponse(result, status=200, safe=True)

        result = {}
        mess = []
        for m in messages:
            msg = {
                'text': m.text,
            }
            mess.append(msg)
        result['messages'] = mess

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})


@csrf_exempt
def password(request, username, password):
    if request.method == 'GET':
        try:
            user = models.User.objects.get(user_name=username, password=password)
            result = {
                'status': 'Spravne heslo'
            }
            return JsonResponse(result, safe=False, status=200, json_dumps_params={'indent': 3})
        except django.core.exceptions.ObjectDoesNotExist:
            result = {
                'status': 'Zle heslo'
            }
            return JsonResponse(result, status=401, safe=False, json_dumps_params={'indent': 3})

    elif request.method == 'PUT':
        user = models.User.objects.get(user_name=username)
        user.password = password
        user.save()
        result = {
            'status': 'Heslo zmenene',
        }
        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})


def find_user(request, username):
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


@csrf_exempt
def upload_file(request, user_id):
    if request.method == 'POST':
        file_name = request.FILES['file']
        params = request.POST.dict()
        path = default_storage.save('materials/' + str(file_name), ContentFile(file_name.read()))

        user = models.User.objects.get(id=user_id)

        if user.user_type_id.type != 1:
            pass

        classroom = models.Classroom.objects.get(id=int(params['classroom_id']))

        material_count = models.Material.objects.count()
        new_material = models.Material.objects.create(id=material_count + 1, classroom_id=classroom
                                                      , name=params['name'], path=path
                                                      , created_at=datetime.datetime.now())
        new_material.save()
        result = {
            'id': new_material.id,
            'created_at': new_material.created_at,
            'teacher': user.first_name + ' ' + user.last_name,
        }

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})
