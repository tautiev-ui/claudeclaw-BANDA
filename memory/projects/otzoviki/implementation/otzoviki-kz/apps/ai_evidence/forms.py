from django import forms

from .models import AIYandexEvidenceLog


class AIYandexEvidenceCaptureForm(forms.ModelForm):
    cited_sources_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="One cited source URL or label per line.",
    )

    class Meta:
        model = AIYandexEvidenceLog
        fields = [
            "company",
            "platform",
            "query",
            "region",
            "answer_excerpt",
            "cited_sources_text",
            "sentiment",
            "visibility",
            "screenshot",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["visibility"].initial = AIYandexEvidenceLog.Visibility.PRIVATE

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("screenshot") and cleaned.get("visibility") == AIYandexEvidenceLog.Visibility.PUBLIC:
            cleaned["visibility"] = AIYandexEvidenceLog.Visibility.PRIVATE
        return cleaned

    def clean_cited_sources_text(self):
        value = self.cleaned_data.get("cited_sources_text", "")
        return [line.strip() for line in value.splitlines() if line.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.cited_sources = self.cleaned_data.get("cited_sources_text", [])
        if commit:
            instance.save()
            self.save_m2m()
        return instance
