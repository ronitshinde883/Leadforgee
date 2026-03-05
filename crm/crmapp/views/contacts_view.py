import json
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models.contact import Contact
from ..decorators import login_is_required

@login_is_required
@csrf_exempt
def get_all_contacts(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    try:
        company = request.user.userprofile.company
        contacts = Contact.objects.filter(company=company)

        contacts_list = []

        for contact in contacts:
            contacts_list.append(
                {
                    "id": contact.id,
                    "name": contact.name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "created_at": contact.created_at,
                }
            )

        return JsonResponse(
            {"message": "Fetched all contacts successfully", "contacts": contacts_list}
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_is_required
@csrf_exempt
def create_contact(request):
    if request.method != "POST":
        return JsonResponse({"error": "post request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "not authenticated user"}, status=401)

    user = request.user
    company = user.userprofile.company

    data = json.loads(request.body)
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    contact = Contact.objects.create(
        owner=user, company=company, name=name, email=email, phone=phone
    )

    return JsonResponse(
        {
            "message": "Contact created successfully",
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
        }
    )

@login_is_required
@csrf_exempt
def update_contact(request, contact_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)

        contact = Contact.objects.get(id=contact_id)
        company = request.user.userprofile.company

        if contact.DoesNotExist:
            return JsonResponse({"error": "Contact does not exists"}, status=404)
        if contact.is_deleted == True:
            return JsonResponse({"error": "Contact already deleted"}, status=400)

        if contact.company != company:
            return JsonResponse(
                {"error": "You cannot edit other company's data"}, status=401
            )

        fields = ["name", "email", "phone"]

        for field in fields:
            if field in data:
                setattr(contact, field, data[field])

        contact.save()

        return JsonResponse(
            {
                "message": "Updated successfully",
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_is_required
@csrf_exempt
def delete_contact(request, contact_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=405)

    contact = Contact.objects.get(id=contact_id)

    if contact.DoesNotExist:
        return JsonResponse({"error": "Contact does not exists"}, status=404)
    if contact.is_deleted == True:
        return JsonResponse({"error": "Contact already deleted"}, status=400)

    company = request.user.userprofile.company

    if contact.company != company:
        return JsonResponse(
            {"error": "Cannot modify another company's data"}, status=401
        )

    contact.is_deleted = True
    contact.save()

    return JsonResponse({"message": "Contact deleted successfully"})

@login_is_required
@csrf_exempt
def get_contact_by_id(request, contact_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    try:
        contact = Contact.objects.get(id=contact_id)
        company = request.user.userprofile.company

        if contact.DoesNotExist:
            return JsonResponse({"error": "Contact does not exists"}, status=404)
        if contact.is_deleted == True:
            return JsonResponse({"error": "Contact already deleted"}, status=400)

        if contact.company != company:
            return JsonResponse(
                {"error": "You cannot view another company's data"}, status=403
            )

        return JsonResponse(
            {
                "message": "Contact fetched successfully",
                "id": contact.id,
                "owner": contact.owner,
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_is_required
@csrf_exempt
def reactivate_contact(request):
    return JsonResponse({"error": "This function is still in hold and in progress"})
