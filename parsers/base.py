import struct, re, math, binascii

class BaseParser:
    def read_file(self, filepath):
        with open(filepath, "rb") as f:
            return f.read()

    def read_cstring(self, raw: bytes, offset: int):
        if offset >= len(raw):
            return "", offset
        end = raw.find(b"\x00", offset)
        if end == -1:
            return raw[offset:].decode("utf-8", errors="replace"), len(raw)
        return raw[offset:end].decode("utf-8", errors="replace"), end + 1

    def hex_spaced(self, data: bytes, limit=None):
        h = binascii.hexlify(data).decode("ascii").upper()
        if limit:
            h = h[:limit*2]
        return " ".join(h[i:i+2] for i in range(0, len(h), 2))

    def find_ascii_runs(self, raw: bytes, min_len=4):
        runs = re.findall(rb"[ -~]{%d,}" % (min_len,), raw)
        return [r.decode("utf-8", errors="replace") for r in runs]

    def extract_null_strings(self, raw: bytes, min_len=2):
        res = []
        i = 0
        L = len(raw)
        while i < L:
            j = raw.find(b"\x00", i)
            if j == -1:
                if L - i >= min_len:
                    seg = raw[i:]
                    res.append((i, seg.decode("utf-8", errors="replace")))
                break
            if j - i >= min_len:
                seg = raw[i:j]
                res.append((i, seg.decode("utf-8", errors="replace")))
            i = j + 1
        return res

    def extract_guids(self, raw: bytes):
        guids = set()
        candidates = self.find_ascii_runs(raw, min_len=8)
        candidates += [s for _, s in self.extract_null_strings(raw, min_len=8)]
        for s in candidates:
            for tok in re.split(r'[^0-9A-Fa-f]', s):
                if len(tok) == 32 and all(c in '0123456789abcdefABCDEF' for c in tok):
                    guids.add(tok.upper())
        return list(guids)

    def ints_uints_floats(self, data: bytes, offset=0, max_items=64):
        ints = []
        uints = []
        floats = []
        L = len(data)
        end = min(L//4*4, offset + 4*max_items)
        for i in range(offset, end, 4):
            try:
                i32 = struct.unpack_from("<i", data, i)[0]
                u32 = struct.unpack_from("<I", data, i)[0]
                f32 = struct.unpack_from("<f", data, i)[0]
            except Exception:
                break
            ints.append(i32)
            uints.append(u32)
            if f32 != f32 or abs(f32) > 1e8:
                floats.append(None)
            else:
                floats.append(round(f32, 6))
        return ints, uints, floats

    def entropy(self, data: bytes):
        if not data:
            return 0.0
        freq = [0]*256
        for b in data:
            freq[b] += 1
        e = 0.0
        L = len(data)
        for c in freq:
            if c == 0:
                continue
            p = c / L
            e -= p * math.log2(p)
        return round(e, 4)

    def make_record(self, raw: bytes, offset: int, length: int):
        seg = raw[offset:offset+length]
        i32, u32, f32 = self.ints_uints_floats(seg, offset=0, max_items=16)
        return {
            "offset": offset,
            "length": length,
            "ascii_text": seg.decode("latin-1", errors="replace"),
            "raw_hex": self.hex_spaced(seg, limit=1024),
            "raw_bytes": seg,
            "int32_values": i32,
            "uint32_values": u32,
            "float32_values": f32,
            "strings": [s for _,s in self.extract_null_strings(seg, min_len=2)],
        }
