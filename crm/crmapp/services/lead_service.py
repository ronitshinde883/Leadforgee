from ..models.lead import Lead
from ..models.contact import Contact
from ..models.deal import Deal
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError


class LeadAlreadyConvertedException(Exception):
    pass


class ContactAlreadyExistsException(Exception):
    def __init__(self, contact_id):
        self.contact_id = contact_id
        super().__init__(f"Contact with this email already exists (id={contact_id})")


@transaction.atomic
def convert_lead(*, lead_id: int, user, create_deal: True, deal_data: dict | None = None):
    """
    Converts a lead into a contact (and optionally a deal).

    Returns:
        dict: {
            "lead": Lead,
            "contact": Contact,
            "deal": Deal | None
        }
    """

    lead = (
        Lead.objects.select_for_update()
        .select_related("company", "user")
        .get(id=lead_id, company=user.userprofile.company)  # multi-tenant isolation
    )

    # already converted
    if lead.converted_to_contact is not None:
        raise LeadAlreadyConvertedException("Lead has already been converted")

    # check email conflicts
    if lead.email:
        existing_contact = Contact.objects.filter(
            company=lead.company, email=lead.email
        ).first()

        if existing_contact:
            raise ContactAlreadyExistsException(existing_contact.id)

    # create contact
    contact = Contact.objects.create(
        company=lead.company,
        owner=lead.owner,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
    )

    deal = None

    # optionally create deal
    if create_deal:
        deal_fields = {
            "company": lead.company,
            "owner": lead.owner,
            "contact": contact,
            "title": f"Deal - {lead.name}",
            "stage": "new",
            "value": getattr(lead, "value", 0) or 0,
        }

        if deal_data:
            deal_fields.update({
                "note": deal_data.get("note"),
            })
            
        deal = Deal.objects.create(**deal_fields)
        
    # update lead
    lead.status = "converted"
    lead.is_archived = True
    lead.converted_at = timezone.now()
    lead.converted_to_contact = contact
    lead.save()

    """
    Activity.objects.create(
        company=lead.company,
        user=user,
        action_type="lead_converted",
        related_object_type="lead",
        related_object_id=lead.id,
        metadata={
            "contact_id": contact.id,
            "deal_id": deal.id if deal else None,
        }
    )
    """

    return {
        "lead": lead,
        "contact": contact,
        "deal": deal
    }