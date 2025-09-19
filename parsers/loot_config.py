import os
from .generic import GenericParser

class LootConfigParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        n = os.path.basename(filename).lower()
        return 'loot_config' in n or 'loot' in n

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        ints = s.get('metadata', {}).get('int_preview', [])
        if ints:
            s['guessed']['weights_preview'] = ints[:8]
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
