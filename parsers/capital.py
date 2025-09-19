import os
from .generic import GenericParser

class CapitalParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return 'capital' in os.path.basename(filename).lower()

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        s['guessed']['type'] = 'capital'
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
