from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models.contact import Contact
<<<<<<< HEAD
from..models.task import Task
from..models.deal import Deal
=======
from ..models.task import Task
from ..models.deal import Deal
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8
from ..models.lead import Lead
from ..models.user import Userprofile
from django.contrib.contenttypes.models import ContentType
import json
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
<<<<<<< HEAD
=======
from ..decorators import login_is_required
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8


@login_is_required
@csrf_exempt
def get_all_tasks(request):
<<<<<<< HEAD
    if request.method != 'POST':
      return JsonResponse({"error": "POST request required"}, status=405)
    try :
      user_company=request.user.Userprofile.company
      #is company ke sare task ayege
      tasks=Task.objects.filter(company=user_company)
      task_list=[]
      
      for task in tasks:#basic operation
        task_list.append({
          "id":task.id,
          "description":task.description,
          "status":task.status,
          "duedate":task.duedate,
          "assignedTo":task.assignedTo.username if task.assignedTo else None
        })
      return JsonResponse({"tasks":task_list},status=200)
    except Exception as e:
      return JsonResponse({"error":str(e)},status=500)
    #aasaaan haiiiiii
      

=======
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)
    try:
        user_company = request.user.userprofile.company
        # is company ke sare task ayege
        tasks = Task.objects.filter(company=user_company)
        task_list = []
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8

        for task in tasks:  # basic operation
            task_list.append(
                {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "duedate": task.duedate,
                    "assignedTo": task.assignedTo.username if task.assignedTo else None,
                }
            )
        return JsonResponse({"tasks": task_list}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    # aasaaan haiiiiii


@login_is_required
@csrf_exempt
def create_task(request):
<<<<<<< HEAD
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)

        model_name = data.get("model_name")
        object_id = data.get("object_id")
        assigned_to_id = data.get("assigned_to")
        description = data.get("description")
        duedate = data.get("duedate")
        status = data.get("status", "pending")

        if not model_name or not object_id or not description or not duedate:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        
        ALLOWED_MODELS = {
            "deal": Deal,
            "lead": Lead,
            "contact": Contact,
        }

        model_class = ALLOWED_MODELS.get(model_name.lower())
        if not model_class:
            return JsonResponse({"error": "Invalid model name"}, status=400)

        try:
            related_object = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            return JsonResponse({"error": "Related object not found"}, status=404)

        user_company = request.user.userprofile.company
        if related_object.company != user_company:
            return JsonResponse({"error": "Unauthorized company access"}, status=403)

        content_type = ContentType.objects.get_for_model(model_class)

        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Assigned user not found"}, status=404)

        parsed_date = parse_date(duedate)
        if not parsed_date:
            return JsonResponse({"error": "Invalid date format (YYYY-MM-DD required)"}, status=400)

        task = Task.objects.create(
            company=user_company,
            assignedTo=assigned_to,
            assignedBy=request.user,
            content_type=content_type,
            object_id=object_id,
            description=description,
            duedate=parsed_date,
            status=status
        )

        return JsonResponse({"message": "Task created successfully"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
=======
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8

    try:
        data = json.loads(request.body)

        model_name = data.get("model_name")
        object_id = data.get("object_id")
        assigned_to_id = data.get("assigned_to")
        description = data.get("description")
        duedate = data.get("duedate")
        status = data.get("status", "pending")

        if not model_name or not object_id or not description or not duedate:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        ALLOWED_MODELS = {
            "deal": Deal,
            "lead": Lead,
            "contact": Contact,
        }

        model_class = ALLOWED_MODELS.get(model_name.lower())
        if not model_class:
            return JsonResponse({"error": "Invalid model name"}, status=400)

        try:
            related_object = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            return JsonResponse({"error": "Related object not found"}, status=404)

        user_company = request.user.userprofile.company
        if related_object.company != user_company:
            return JsonResponse({"error": "Unauthorized company access"}, status=403)

        content_type = ContentType.objects.get_for_model(model_class)

        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Assigned user not found"}, status=404)

        parsed_date = parse_date(duedate)
        if not parsed_date:
            return JsonResponse(
                {"error": "Invalid date format (YYYY-MM-DD required)"}, status=400
            )

        task = Task.objects.create(
            company=user_company,
            assignedTo=assigned_to,
            assignedBy=request.user,
            content_type=content_type,
            object_id=object_id,
            description=description,
            duedate=parsed_date,
            status=status,
        )

        return JsonResponse({"message": "Task created successfully"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_is_required
@csrf_exempt
<<<<<<< HEAD
def update_task(request,task_id):
    if request.method!='POST':
      return JsonResponse({"error":"post request required"},status=405)
    
    try:
      data=json.loads(request.body)
      #lets lake all task 1
      try:
        task=Task.objects.get(id=task_id)
      except Task.DoesNotExist:
        data=json.loads(request.data)
      user_company=request.user.userprofile.company
      if task.company!=user_company:
        return JsonResponse({"error": "Unauthorized access"}, status=403)
      
      #this fields can be updated samjha kya lala?
      description=data.get("description")
      duedate=data.get("duedate")
      status=data.get("status")
      assigned_to_id=data.get("assigned_to")
      
      if description:
        task.description=description
      if duedate:
        parsed_date=parse_date(duedate)
        if not parsed_date:
          return JsonResponse({"error": "Invalid date format (YYYY-MM-DD required)"}, status=400) 
        task.duedate=duedate
      if status:
        task.status=status 
      
    allowed_fields = ["description", "duedate", "status", "assigned_to_id"]

    for field in allowed_fields:
        if field in data:
            setattr(task, field, data[field])
      if assigned_to_id is not None:
        if assigned_to_id=="":
          task.assignedTo=None #this will work when user will erase the old assigned person and enters nothing 
        else:
          try:
            assigned_user=User.objects.get(id=assigned_to_id)
            task.assignedTo=assigned_user
          except User.DoesNotExist:
            return JsonResponse({"error": "Assigned user not found"}, status=404)
      task.save()
      return JsonResponse({"message": "Task updated successfully"}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)#here e the any specific error
        
  
=======
def update_task(request, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "post request required"}, status=405)
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8

    try:
        data = json.loads(request.body)
        # lets lake all task 1
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
        
        user_company = request.user.userprofile.company
        if task.company != user_company:
            return JsonResponse({"error": "Unauthorized access"}, status=403)

        fields = ["description", "duedate", "status", "assigned_to"]

        for field in fields:
            if field in data:
                setattr(task, field, data[field])
        task.save()
        return JsonResponse({"message": "Task updated successfully"}, status=200)

    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=500
        )  # here e the any specific error


@login_is_required
@csrf_exempt
<<<<<<< HEAD
def delete_task(request,task_id):
    if request.method!='POST':
      return JsonResponse({"error":"post request required"},status=405)
    try:
      try:
        task=Task.objects.get(id=task_id)
      except Task.DoesNotExist:
        return JsonResponse({"error":"Task not found"},status=404)
      user_company=request.user.Userprofile.company 
      if task.company!=user_company:
        return JsonResponse({"error":"Unauthorized access"},status=403)
      
      task.delete()
      return JsonResponse({"message":"task deleted successfully"},status=200)
    
    except Exception as e :
      return JsonResponse({"error":str(e)},status=500)
=======
def delete_task(request, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "post request required"}, status=405)
    try:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
        user_company = request.user.userprofile.company
        if task.company != user_company:
            return JsonResponse({"error": "Unauthorized access"}, status=403)
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8

        task.delete()
        return JsonResponse({"message": "task deleted successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_is_required
@csrf_exempt
<<<<<<< HEAD
def get_task_by_id(request,task_id):#ye pura khudse kiya hai thoda goThrough karna padega
    if request.method!='POST':
      return JsonResponse({"error":"post request required"},status=405)
    try :
      data=json.loads(request.body)
      try:
        task=Task.objects.get(id=task_id)
      except Task.DoesNotExist:
        return JsonResponse({"error":"Task not found"},status=404)
      user_company=request.user.Userprofile.company
      if task.company!=user_company:
        return JsonResponse({"error":"Unauthorized access"},status=403)
      
      return JsonResponse({
        "id" :task.id,
        "description":task.description,
        "status":task.status,
        "duedate":task.duedate,
        "assignedTo":task.assignedTo.username if task.assignedTo else None
      },status=200)
    except Exception as e :
      return JsonResponse({"error":str(e)},status=500)
=======
def get_task_by_id(
    request, task_id
):  # ye pura khudse kiya hai thoda goThrough karna padega
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)
    try:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
        user_company = request.user.userprofile.company
        if task.company != user_company:
            return JsonResponse({"error": "Unauthorized access"}, status=403)

        return JsonResponse(
            {
                "id": task.id,
                "description": task.description,
                "status": task.status,
                "duedate": task.duedate,
                "assignedTo": task.assignedTo.username if task.assignedTo else None,
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_is_required
>>>>>>> 1999865af63d114769982df3e4e500fe69102ff8
@csrf_exempt
def reactivate_task(request):
    return JsonResponse({"error": "This function is still in hold and in progress"})
