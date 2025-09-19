import os
from .generic import GenericParser

class AnimupdaterateparamsParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return 'animupdaterateparams' in os.path.basename(filename).lower()

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        s['guessed']['type'] = 'animupdaterateparams'
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
