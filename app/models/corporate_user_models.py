from tortoise import fields, models


class CorporateUser(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "app.models.BaseUser", related_name="corporate_profiles"
    )
    company_name = fields.CharField(max_length=255, null=False)
    business_start_date = fields.DatetimeField(null=False)
    business_number = fields.CharField(max_length=20, null=False, unique=True)
    company_description = fields.TextField(null=True)
    manager_name = fields.CharField(max_length=100, null=False)
    manager_phone_number = fields.CharField(max_length=20, null=False)
    manager_email = fields.CharField(max_length=255, null=True, unique=True)

    class Meta:
        table = "CORPORATE_USER"
