from tortoise import fields, models


class SeekerUser(models.Model):
    STATUS_SEEKING = "seeking"
    STATUS_EMPLOYED = "employed"
    STATUS_NOT_SEEKING = "not_seeking"

    STATUS_CHOICES = [
        (STATUS_SEEKING, "seeking"),
        (STATUS_EMPLOYED, "employed"),
        (STATUS_NOT_SEEKING, "not_seeking"),
    ]

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("app.models.BaseUser", related_name="seeker_profiles")
    name = fields.CharField(max_length=20, null=False)
    phone_number = fields.CharField(max_length=20, null=False)
    age = fields.IntField(null=False)
    interests = fields.JSONField(null=False)
    purposes = fields.JSONField(null=False)
    sources = fields.JSONField(null=True)
    applied_posting = fields.JSONField(null=True)
    applied_posting_count = fields.IntField(null=False, default=0)
    is_social = fields.BooleanField(default=False)
    status = fields.CharField(
        max_length=20,
        null=False,
        choices=STATUS_CHOICES,
        default=STATUS_SEEKING,
    )
    interested_companies = fields.ManyToManyField(
        "app.models.CorporateUser",
        related_name="interested_seekers",
        through="interested_companies_seeker",
    )

    class Meta:
        table = "SEEKER_USER"
