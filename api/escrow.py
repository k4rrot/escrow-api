from datetime import datetime

from flask import current_app, Blueprint, request, make_response, jsonify
from mongoengine.errors import DoesNotExist
import requests

from models.record import EscrowRecord


escrow = Blueprint('escrow', __name__, url_prefix='/escrow')


def resolve_escrow_record(record: EscrowRecord):
    disclose = True if record.release_date else False
    return {
        'id': str(record.id),
        'name': record.name,
        'data': record.key if disclose else None,
        'payment_address': record.payment_address,
        'release_amount': record.release_amount,
        'create_date': record.create_date.isoformat(),
        'release_date': record.release_date.isoformat() if disclose else None,
    }


def check_address(address: str, amount: float, method: str):
    if method == 'sochain':
        resp = requests.get(
            'https://sochain.com/api/v2/get_address_balance/BTC/{}'.format(
                address
            )
        )

        if resp.status_code != 200:
            return False

        balance = float(
            resp.json().get('data', {}).get('confirmed_balance', 0)
        )

        if balance >= amount:
            return True

    # Default to unverified
    return False


@escrow.route('/', defaults={'escrow_id': None}, methods=['GET'])
@escrow.route('/<escrow_id>', methods=['GET'])
def get_escrow(escrow_id):
    # get all escrow records
    if not escrow_id:
        skip = request.args.get('skip', 0)
        take = request.args.get('take', 100)

        all_records = EscrowRecord.objects() \
                                  .order_by('create_date') \
                                  .skip(skip).limit(take)

        return make_response(
            jsonify([resolve_escrow_record(i) for i in all_records]),
            200,
        )

    # Attempt to retrieve record
    try:
        record = EscrowRecord.objects.get(id=escrow_id)

        if check_address(
            record.payment_address,
            record.release_amount,
            current_app.config.get(
                'ADDRESS_VERIFY_METHOD',
            ),
         ):
            # Release key
            record.modify(release_date=datetime.now())

            return make_response(
                jsonify(
                    resolve_escrow_record(record)
                ),
                200
            )

        else:
            return make_response(
                jsonify(
                    resolve_escrow_record(record)
                ),
                200
            )

    except DoesNotExist:
        return make_response('', 404)


@escrow.route('/', methods=['POST'])
def create_escrow():
    args = request.json

    escrow = {
        'name': args.get('name')[:256],
        'key': args.get('data'),
        'payment_address': args.get('address'),
        'release_amount': args.get('amount'),
    }

    if None in list(escrow.keys()):
        return make_response(
            jsonify(
                {'err': 'name, key, address, and amount are required'}
            ),
            400,
        )

    new_escrow = EscrowRecord(**escrow)
    new_escrow.save()

    escrow['id'] = str(new_escrow.id)

    return make_response(
        jsonify(escrow),
        200,
    )
