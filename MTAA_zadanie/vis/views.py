import django.core.exceptions
from django.shortcuts import render
from django.http import JsonResponse
from . import models
# Create your views here.


def login(request, username, password):
    try:
        user = models.User.objects.get(user_name=username, password=password)

        # user_type = models.UserType.objects.values().get(id=user['user_type_id_id'])

        u = user.user_type_id

        messages = models.Message.objects.filter(receiver_id=user.id)
        count = messages.count() if messages.count() < 3 else 2

        msgs = []
        for i in range(count):
            receiver = models.User.objects.get(id=messages[i].sender_id)
            msg = {
                'message_sender': receiver.first_name + ' ' + receiver.last_name,
                'message_name': messages[i].name,
                'created_at': messages[i].created_at,
            }
            msgs.append(msg)

        materials = models.Material.objects.filter(teacher_id=user.id)
        count2 = materials.count() if materials.count() < 3 else 2

        mtrs = []
        for i in range(count2):
            receiver = models.User.objects.get(id=materials[i].teacher_id)
            mtr = {
                'material_sender': receiver.first_name + ' ' + receiver.last_name,
                'material_name': materials[i].name,
                'created_at': materials[i].created_at,
            }
            mtrs.append(mtr)

        result = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_name': user.user_name,
            'user_type_id': u.id,
            'messages': msgs,
            'materials': mtrs,
        }

        return JsonResponse(result, status=200, safe=False, json_dumps_params={'indent': 3})
    except django.core.exceptions.ObjectDoesNotExist:

        return JsonResponse({'res': 'foo'}, safe=False, status=200)
