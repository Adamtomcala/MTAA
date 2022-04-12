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

numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
alfabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


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

                return JsonResponse(result, safe=False, status=400, json_dumps_params={'indent': 3})
            except django.core.exceptions.ObjectDoesNotExist:
                result = {
                    'status': 'Nespravne meno',
                }

                return JsonResponse(result, safe=False, status=401, json_dumps_params={'indent': 3})


# Asi hotovo
@csrf_exempt
def message(request):
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

    # Tento POST request sluzi na spracovanie odoslania spravy pouzivatelovi
    elif request.method == 'POST':
        try:
            params = request.POST.dict()
            receiver = models.User.objects.get(user_name=params['user_name'])
            sender = models.User.objects.get(id=params['sender_id'])

            now = datetime.datetime.now()
            new_message = models.Message.objects.create(sender=sender, receiver=receiver, name=params['name'],
                                                        text=params['text'], created_at=now)
            new_message.save()

            result = {
                'status': 'Odoslane',
            }

            return JsonResponse(result, status=200, safe=False)
        # Ak prijimatel neexistuje
        except django.core.exceptions.ObjectDoesNotExist:
            result = {
                'status': 'Pouzivatel neexistuje',
            }
            return JsonResponse(result, status=404, safe=False)


def check_password(pswd, req):
    for element in req:
        if element in pswd:
            return True
    return False


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

        # Ak sa stare a nove heslo bude zhodovat
        if password == user.password:
            result = {
                'status': 'Hesla sa zhoduju',
            }
            return JsonResponse(result, status=403, safe=False, json_dumps_params={'indent': 3})

        # Kontrloa dlzky hesla
        if len(password) < 8:
            result = {
                'status': 'Heslo musi mat aspon 8 znakov',
            }
            return JsonResponse(result, status=403, safe=False)

        # Kontrola ci heslo obsahuje velke pismeno
        if not check_password(password, alfabet):
            result = {
                'status': 'Heslo neobsahuje velke pismeno',
            }
            return JsonResponse(result, status=403, safe=False, json_dumps_params={'indent': 3})

        # Kontrola ci heslo obsahuje cislicu
        if not check_password(password, numbers):
            result = {
                'status': 'Heslo neobsahuje cislicu',
            }
            return JsonResponse(result, status=403, safe=False, json_dumps_params={'indent': 3})

        user.password = password
        user.save()
        result = {
            'status': 'Heslo zmenene',
        }
        return JsonResponse(result, status=201, safe=False, json_dumps_params={'indent': 3})


# Asi hotovo
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
    # Funkcia sluzi na spracovanie GET/POST requestu
    # Kvoli akceptacnym testom, bude tam nejaky button, ktory zavola tento predment,
    # Ak bude pouzivatel student vyskoci hlaska o nepovolenie

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
        flag = False
        for extension in file_extensions:
            name = str(file_name)
            if extension == name[len(name) - len(extension):]:
                flag = True
                break

        if not flag:
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


@csrf_exempt
def delete_file(request, material_id):
    # Tento Delete sluzi na odstranenie materialu z classroomy
    # Ak bude pouzivatel ucitel, tak hlaska o potvrdenie pridania/vymazanie materialu

    if request.method == 'DELETE':
        material = models.Material.objects.get(id=material_id)

        result = {
            'material_name': material.name,
        }

        os.remove(material.path)
        material.delete()

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})


def materials(request):
    # Tato funkcia bude sluzit na spracovanie requestu na zobrazenie materialov pouzivatela
    if request.method == 'GET':
        params = request.GET.dict()

        fromm, to = (int(params['page']) - 1) * 5, (int(params['page'])) * 5

        classrooms = models.ClassroomUser.objects.filter(user_id=int(params['id']))

        m = []
        for classroom in classrooms:
            mts = models.Material.objects.filter(classroom_id=classroom.classroom.id)
            for mt in mts:
                m.append(mt)

        final_materials = m[fromm:to]

        result = {}
        material_result = []
        for mat in final_materials:
            material_result.append({
                'name': mat.name,
                'created_at': mat.created_at,
            })

        result['materials'] = material_result

        return JsonResponse(result, status=200, safe=False)


# Asi hotovo
@csrf_exempt
def registration(request):
    if request.method == 'POST':
        params = request.POST.dict()
        # Uz sa v databaze taky pouzivatel nachadza
        try:
            user = models.User.objects.get(user_name=params['user_name'])

            result = {
                'status': f"Pouzivatel %s uz existuje." % user.user_name,
            }

            return JsonResponse(result, status=401, safe=False)
        # Registracia pouzivatela
        except django.core.exceptions.ObjectDoesNotExist:
            user_type = models.UserType.objects.get(type=params['type'])

            # Kontrloa dlzky hesla
            if len(params['password']) < 8:
                result = {
                    'status': 'Heslo musi mat aspon 8 znakov',
                }
                return JsonResponse(result, status=403, safe=False)

            # Kontrola ci heslo obsahuje velke pismeno
            if not check_password(params['password'], alfabet):
                result = {
                    'status': 'Heslo neobsahuje velke pismeno.',
                }
                return JsonResponse(result, status=403, safe=False)

            # Kontrola ci heslo obsahuje cislicu
            if not check_password(params['password'], numbers):
                result = {
                    'status': 'Heslo neobsahuje cislicu',
                }
                return JsonResponse(result, status=403, safe=False)

            new_user = models.User.objects.create(user_type_id=user_type, first_name=params['first_name'],
                                                  last_name=params['last_name'], user_name=params['user_name'],
                                                  password=params['password'], email=params['email'],
                                                  id_school=['id_school'], phone=['phone'])
            new_user.save()

            result = {
                'Status': 'Uspesna registracia',
            }

            return JsonResponse(result, status=200, safe=False)


# navrh na akceptacny test
# Asi hotovo
@csrf_exempt
def add_student_to_classroom(request, classroom_name, user_name, teacher_name):
    # Pridanie studenta do triedy
    if request.method == 'GET':
        user = models.User.objects.get(user_name=teacher_name)

        if user.user_type_id.id == 1:
            result = {
                'status': 'Povolene',
            }
            return JsonResponse(result, status=200, safe=False)

        result = {
            'status': 'Nepovolene',
        }
        return JsonResponse(result, status=403, safe=False)

    elif request.method == 'POST':
        # Ak zadany pouzivatel existuje
        try:
            user = models.User.objects.get(user_name=user_name)
            classroom = models.Classroom.objects.get(lecture_name=classroom_name)
            # Ak zadany pouzivatel neexistuje
        except django.core.exceptions.ObjectDoesNotExist:
            result = {
                'status': 'Pouzivatel neexistuje',
            }
            return JsonResponse(result, status=403, safe=False)

        # Ak uz je pouzivatel v triede
        if models.ClassroomUser.objects.filter(user=user.id, classroom=classroom.id).exists():
            result = {
                'status': 'Pouzivatel sa v triede nachadza',
            }
            return JsonResponse(result, status=403, safe=False)

        # Ak sa pouzivatel v triede nenachadza
        new_classroom_user = models.ClassroomUser.objects.create(user=user, classroom=classroom)
        new_classroom_user.save()

        result = {
            'status': 'Uspesne pridany',
        }

        return JsonResponse(result, status=201, safe=False)

    # Odstranenie studenta z triedy
    elif request.method == 'DELETE':
        classroom = models.Classroom.objects.get(lecture_name=classroom_name)
        user = models.User.objects.get(user_name=user_name)
        classroom_user = models.ClassroomUser.objects.get(classroom=classroom, user=user)

        classroom_user.delete()

        result = {
            'status': 'Uspesne odstraneny',
        }

        return JsonResponse(result, status=200, safe=False)


# Asi hotovo
def return_classroom_users(request, classroom_name):
    if request.method == 'GET':
        classroom = models.Classroom.objects.get(lecture_name=classroom_name)

        classes = models.ClassroomUser.objects.filter(classroom=classroom)

        users = []

        for c in classes:
            if c.user.user_type_id.id == 1:
                continue
            user = {
                'name': c.user.first_name + ' ' + c.user.last_name,
            }
            users.append(user)
        result = {
            'users': users,
        }

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})
