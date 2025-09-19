import os
from .base import BaseParser

class GenericParser(BaseParser):
    @staticmethod
    def can_parse(filename: str, raw: bytes) -> bool:
        return True

    def parse_bytes(self, raw: bytes):
        header = {}
        if len(raw) >= 4:
            header['magic'] = raw[:4].decode('ascii', errors='replace').strip('\x00')
        if len(raw) >= 8:
            header['uint32_at_4'] = int.from_bytes(raw[4:8], 'little')

        strings = self.extract_null_strings(raw, min_len=3)
        ascii_runs = self.find_ascii_runs(raw, min_len=4)
        guids = self.extract_guids(raw)
        i32, u32, f32 = self.ints_uints_floats(raw, offset=0, max_items=128)

        cand = set([0, len(raw)])
        for off, s in strings:
            cand.add(off); cand.add(off+len(s))
        for s in ascii_runs:
            try:
                o = raw.find(s.encode('utf-8'))
                if o >= 0:
                    cand.add(o); cand.add(o+len(s))
            except Exception:
                pass
        for g in guids:
            try:
                pos = raw.find(bytes.fromhex(g))
                if pos >= 0:
                    cand.add(pos); cand.add(pos+16)
            except Exception:
                pass

        if len(raw) > 512:
            for step in (16,32,64):
                if len(raw) // step > 2:
                    for i in range(0, len(raw), step):
                        cand.add(i); cand.add(min(i+step, len(raw)))
        offsets = sorted([o for o in cand if 0<=o<=len(raw)])
        merged = []
        for o in offsets:
            if not merged or o - merged[-1] > 2:
                merged.append(o)
        offsets = merged

        records = []
        for i in range(len(offsets)-1):
            a = offsets[i]; b = offsets[i+1]
            if a>=b: continue
            rec = self.make_record(raw, a, b-a)
            rec['type'] = 'segment'
            rec['guids'] = [g for g in guids if raw.find(bytes.fromhex(g))>=a and raw.find(bytes.fromhex(g))<b]
            records.append(rec)

        if not records:
            rec = self.make_record(raw, 0, len(raw))
            rec['type']='full'
            records.append(rec)

        structured = {
            'file': None,
            'size': len(raw),
            'header': header,
            'records': records,
            'strings': [s for _,s in strings] + ascii_runs,
            'guids': guids,
            'metadata': {
                'entropy': self.entropy(raw),
                'string_count': len(strings) + len(ascii_runs),
                'guid_count': len(guids),
                'int_preview': i32[:32],
                'float_preview': f32[:32]
            }
        }
        return {'raw': raw, 'structured': structured}

    def parse(self, filepath: str):
        raw = self.read_file(filepath)
        res = self.parse_bytes(raw)
        res['structured']['file'] = os.path.basename(filepath)
        return res

    def to_bytes(self, data) -> bytes:
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)
        if isinstance(data, dict) and 'raw' in data and isinstance(data['raw'], (bytes, bytearray)):
            return data['raw']
        recs = None
        if isinstance(data, dict) and 'structured' in data:
            recs = data['structured'].get('records', [])
        elif isinstance(data, dict) and 'records' in data:
            recs = data.get('records', [])
        out = bytearray()
        if recs:
            for r in recs:
                hx = r.get('raw_hex', '')
                if hx:
                    try:
                        out += bytes.fromhex(hx.replace(' ', ''))
                    except Exception:
                        pass
        if out:
            return bytes(out)
        raise ValueError('Cannot build bytes from provided structured data')
