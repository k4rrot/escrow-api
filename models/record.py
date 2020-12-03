from datetime import datetime
from uuid import uuid4

from mongoengine import Document, fields


class EscrowRecord(Document):
    id = fields.UUIDField(primary_key=True, default=uuid4)
    key = fields.StringField()
    name = fields.StringField()
    payment_address = fields.StringField()
    release_amount = fields.FloatField()
    create_date = fields.DateTimeField(default=datetime.now)
    release_date = fields.DateTimeField()
