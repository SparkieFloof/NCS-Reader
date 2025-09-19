import os
from .generic import GenericParser

class InvNamePartParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return 'inv_name_part' in os.path.basename(filename).lower()

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        if s.get('strings'):
            s['guessed']['display_name'] = max(s['strings'], key=len)
        if s.get('guids'):
            s['guessed']['primary_guid'] = s['guids'][0]
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
