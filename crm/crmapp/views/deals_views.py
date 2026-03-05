import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import User
from ..models.common import Company
from ..models.user import Userprofile
from django.shortcuts import render, redirect
from .auth_views import login_user
from ..models.deal import Deal
from ..models.contact import Contact
from ..decorators import login_is_required, role_required


@login_is_required
@csrf_exempt
def create_deal(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    data = json.loads(request.body)
    title = data.get("title")
    value = data.get("value")
    stage = data.get("stage")
    expected_closed_date = data.get("closedate")
    note = data.get("note")
    profile = request.user.userprofile
    company = profile.company
    owner = request.user

    with transaction.atomic():
        Deal.objects.create(
            owner=owner,
            company=company,
            title=title,
            value=value,
            stage=stage,
            expected_closed_date=expected_closed_date,
            note=note,
        )

    return JsonResponse({"message": "Deal created successfully"}, status=201)


@login_is_required
@csrf_exempt
def get_all_deals(request):

    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=400)

    deals = Deal.objects.filter(owner=request.user).select_related("company", "contact")

    deal_data = []

    for deal in deals:
        deal_data.append(
            {
                "id": deal.id,
                "company_id": deal.company.id,
                "company_name": deal.company.title,
                # "contact_id": deal.contact.id,
                # "contact_name": deal.contact.name,  # change if different field ok beta samja kyaaaaaa
                "value": deal.value,
                "stage": deal.stage,
                "expected_closed_date": str(deal.expected_closed_date),
                "note": deal.note,
                "created_at": str(deal.created_at),
            }
        )

    return JsonResponse({"deals": deal_data}, status=200)


@login_is_required
@csrf_exempt
def update_deal(request, deal_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})

    try:
        company = request.user.userprofile.company
        deal = Deal.objects.get(id=deal_id)
        if not deal:
            return JsonResponse({"error": "Deal does not exists"}, status=404)

        if deal.company != company:
            return JsonResponse(
                {"error": "You cannot modify other company's data"}, status=401
            )

        data = json.loads(request.body)
        fields = ["title", "value", "stage", "expected_closed_date", "note"]

        for field in fields:
            if field in data:
                setattr(deal, field, data[field])

        return JsonResponse(
            {
                "message": "Updated deal successfully",
                "title": deal.title,
                "value": deal.value,
                "stage": deal.value,
                "expected_close_date": deal.expected_closed_date,
                "note": deal.note,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_is_required
@csrf_exempt
def get_deal_by_id(request, deal_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    try:
        deal = Deal.objects.get(id=deal_id)

        if not deal:
            return JsonResponse({"error": "Deal does not exists"}, status=404)

        company = request.user.userprofile.company
        if deal.company != company:
            return JsonResponse(
                {"error": "Cannot modify other company's data"}, status=400
            )

        return JsonResponse(
            {
                "message": "Fetched deal successfully",
                "title": deal.title,
                "value": deal.value,
                "stage": deal.stage,
                "expected_closed_date": deal.expected_closed_date,
                "note": deal.note,
                "created_at": deal.created_at
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def delete_deal(request):
    pass


@csrf_exempt
def reactivate_deal(request):
    pass
