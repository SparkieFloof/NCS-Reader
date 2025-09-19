import os
from .generic import GenericParser as _Generic

class LootParser(_Generic):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return "loot" in os.path.basename(filename).lower()

    def parse(self, filepath: str):
        base = super().parse(filepath)
        s = base['structured']
        s.setdefault('guessed', {})
        if s.get('strings'):
            s['guessed']['primary_string'] = s['strings'][0]
        if 'loot' == 'inv_name_part' and s.get('guids'):
            s['guessed']['inv_guid'] = s['guids'][0]
        s['metadata'] = s.get('metadata', {})
        s['metadata']['parsed_by'] = 'LootParser'
        return {'structured': s, 'raw_bytes': base['raw_bytes']}

    def to_bytes(self, data: dict) -> bytes:
        if isinstance(data, (bytes, bytearray)):
            return data
        if 'raw_bytes' in data and isinstance(data['raw_bytes'], (bytes, bytearray)):
            return data['raw_bytes']
        return super().to_bytes(data)
