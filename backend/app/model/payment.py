from typing import Dict
from app.model.rwmodel import RWModel

class CryptoPaymentMethod(RWModel):
    ''' User's crypto wallet validation model'''
    walletsAddress: Dict[str, str] # like {'Tezos': 'tz1SFCkgy9TkU2bP8xYLR8nokSFjDZykz3Lq', 'Eth': '0x1649053e57E89934De495147fb8Fa9689a55DD40'}