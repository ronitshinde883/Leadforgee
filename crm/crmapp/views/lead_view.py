from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models.contact import Contact
from ..decorators import role_required
from ..services.lead_service import convert_lead
from ..services.lead_service import (
    LeadAlreadyConvertedException,
    ContactAlreadyExistsException
)
from ..models.lead import Lead
from ..decorators import login_is_required

@login_is_required
@csrf_exempt
def get_all_leads(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    user = request.user
    company = user.userprofile.company

    leads = Lead.objects.filter(company=company, is_archived=False)

    data = [
        {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,    
            "status": lead.status
        }
        for lead in leads
    ]

    return JsonResponse({"leads": data})

@login_is_required
@csrf_exempt
def create_lead(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    user = request.user
    company = user.userprofile.company

    try:
        data = json.loads(request.body)

        lead = Lead.objects.create(
            company=company,
            owner = user,
            name = data.get("name"),
            email = data.get("email"),
            phone = data.get("phone"),
            source = data.get("source"),
            status="new",
            value = data.get("value"),
            note = data.get("note")
        )

        return JsonResponse({
            "message": "Lead created successfully",
            "lead_id": lead.id
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_is_required
@csrf_exempt
def update_lead(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    company = request.user.userprofile.company

    lead = get_object_or_404(
        Lead,
        id=pk,
        company=company
    )

    if lead.status == "converted":
        return JsonResponse(
            {"error": "Converted leads cannot be edited"}, status=400
        )
    
    data = json.loads(request.body)

    lead.name = data.get("name", lead.name)
    lead.email = data.get("email", lead.email)
    lead.phone = data.get("phone", lead.phone)
    lead.status = data.get("status", lead.status)
    lead.value = data.get("value", lead.value)
    lead.note = data.get("note", lead.note)
    lead.save()

    return JsonResponse({"message": "Lead updated successfully"})

@login_is_required
@csrf_exempt
def delete_lead(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    company = request.user.userprofile.company
    lead = get_object_or_404(
        Lead,
        id=pk,
        company = company
    )

    lead.is_archived = True
    lead.save()

    return JsonResponse({"message": "Lead archived successfully"})

@login_is_required
@csrf_exempt
def get_lead_by_id(request, pk):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    company = request.user.userprofile.company

    lead = get_object_or_404(
        Lead,
        id=pk,
        company=company
    )

    return JsonResponse({
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "status": lead.status
    })

@login_is_required
@csrf_exempt
def reactivate_lead(request):
    return JsonResponse({"error": "This function is still in hold and in progress"})

@login_is_required
@csrf_exempt
@role_required(["admin", "manager"])
def converting_lead(request, pk):   # ON-HOLD IN-PROGRESS
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)
    
    data = json.loads(request.body) if request.body else {}
    user = request.user

    try:
        create_deal = data.get("create_deal", True)
        deal_note = data.get("note")

        result = convert_lead(
            lead_id=pk,
            user=request.user,
            create_deal=create_deal,
            deal_data={"note": deal_note}

        )
    except LeadAlreadyConvertedException:
        pass
    except ContactAlreadyExistsException:
        pass