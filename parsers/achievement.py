import os
from .generic import GenericParser

class AchievementParser(GenericParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return 'achievement' in os.path.basename(filename).lower()

    def parse_bytes(self, raw: bytes):
        res = super().parse_bytes(raw)
        s = res['structured']
        s.setdefault('guessed', {})
        if len(raw) >= 12:
            try:
                magic = raw[:4].decode('ascii', errors='replace').strip('\x00')
                ver = int.from_bytes(raw[4:8], 'little')
                cnt = int.from_bytes(raw[8:12], 'little')
                s['header']['magic_guess'] = magic
                s['header']['version_guess'] = ver
                s['header']['entry_count_guess'] = cnt
            except Exception:
                pass
        return res

    def to_bytes(self, data):
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return super().to_bytes(data)
