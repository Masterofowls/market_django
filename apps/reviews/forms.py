"""Storefront review and feedback forms."""

from __future__ import annotations

from django import forms

from apps.reviews.models import Comment, Review


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        coerce=int,
        choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")],
        widget=forms.RadioSelect(attrs={"class": "star-rating-input"}),
        label="Your rating",
    )

    class Meta:
        model = Review
        fields = ("rating", "title", "body")
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Summary (optional)", "maxlength": 160}
            ),
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Share details about battery, camera, build…",
                }
            ),
        }
        labels = {
            "title": "Review title",
            "body": "Your feedback",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Ask a question or leave a short note…"}
            ),
        }
        labels = {"body": "Comment"}
