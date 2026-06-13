from django import forms

from apps.business.models import BusinessAccount, BusinessRepresentative, ClaimProfileRequest, OfficialResponse, ReputationAuditLead
from apps.companies.models import Company


SURFACE_CHOICES = [
    ("otzoviki", "Otzoviki"),
    ("yandex", "Yandex"),
    ("2gis", "2GIS"),
    ("google", "Google"),
    ("ai", "AI answers"),
]


class CompanySlugMixin(forms.Form):
    company_slug = forms.SlugField(label="Company slug")

    def clean_company_slug(self):
        slug = self.cleaned_data["company_slug"]
        try:
            return Company.objects.get(slug=slug)
        except Company.DoesNotExist as exc:
            raise forms.ValidationError("Компания не найдена") from exc


def safe_internal_source_path(request, fallback: str) -> str:
    referer = request.META.get("HTTP_REFERER", "") if request is not None else ""
    if not referer:
        return fallback
    try:
        from urllib.parse import urlparse

        parsed = urlparse(referer)
    except ValueError:
        return fallback
    if parsed.netloc and parsed.netloc != request.get_host():
        return fallback
    path = parsed.path or fallback
    return path if path.startswith("/") else fallback


class ClaimProfileRequestForm(CompanySlugMixin, forms.ModelForm):
    class Meta:
        model = ClaimProfileRequest
        fields = ["contact_name", "contact_email", "phone", "proof_note", "consent_given"]

    def save(self, commit=True, *, request=None):
        claim = super().save(commit=False)
        claim.company = self.cleaned_data["company_slug"]
        claim.source_page = safe_internal_source_path(request, "/claim-profile/")
        if commit:
            claim.save()
        return claim


class ReputationAuditLeadForm(CompanySlugMixin, forms.ModelForm):
    requested_surfaces = forms.MultipleChoiceField(choices=SURFACE_CHOICES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = ReputationAuditLead
        fields = ["contact_name", "contact_email", "phone", "requested_surfaces", "consent_given"]

    def save(self, commit=True, *, request=None):
        lead = super().save(commit=False)
        lead.company = self.cleaned_data["company_slug"]
        lead.source_page = safe_internal_source_path(request, "/reputation-audit/")
        lead.requested_surfaces = self.cleaned_data["requested_surfaces"]
        if commit:
            lead.save()
        return lead


class OfficialResponseSubmissionForm(forms.Form):
    contact_name = forms.CharField(max_length=160)
    contact_email = forms.EmailField()
    role_title = forms.CharField(max_length=120, required=False)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))

    def save(self, *, company: Company, request=None) -> OfficialResponse:
        account, _ = BusinessAccount.objects.get_or_create(
            company=company,
            defaults={"display_name": f"{company.name} Business"},
        )
        representative = None
        submitted_email = self.cleaned_data["contact_email"]
        authenticated_email = getattr(getattr(request, "user", None), "email", "") if request is not None else ""
        if authenticated_email:
            representative = BusinessRepresentative.objects.filter(
                account=account,
                email__iexact=authenticated_email,
                verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
                email_verified=True,
            ).first()
        if representative is None and not BusinessRepresentative.objects.filter(account=account, email__iexact=submitted_email, verification_status=BusinessRepresentative.VerificationStatus.APPROVED, email_verified=True).exists():
            representative, _ = BusinessRepresentative.objects.get_or_create(
                account=account,
                email=submitted_email,
                defaults={
                    "full_name": self.cleaned_data["contact_name"],
                    "role_title": self.cleaned_data.get("role_title", ""),
                },
            )
        return OfficialResponse.objects.create(
            company=company,
            representative=representative,
            body=self.cleaned_data["body"],
            status=OfficialResponse.Status.PENDING,
            source_page=safe_internal_source_path(request, company.get_absolute_url()),
        )
