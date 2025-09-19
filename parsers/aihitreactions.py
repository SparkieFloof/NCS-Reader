import os
from .generic import GenericParser

class AihitreactionsParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        n = os.path.basename(filename).lower()
        return 'aihit' in n or 'aihitreactions' in n

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        s['guessed']['approx_entries'] = max(1, len(raw)//64)
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
