import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from parsers import get_parser_for

class HexEditor(tk.Text):
    def __init__(self, parent, data: bytes, on_change=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data = bytearray(data)
        self.on_change = on_change
        self.configure(font=("Courier New", 10), undo=True, wrap="none", padx=4, pady=4)
        self.insert("1.0", self.format_hex(self.data))
        self.bind("<KeyRelease>", self.on_edit)
        self.bind("<Button-1>", self.prevent_offset_edit)

    def format_hex(self, data: bytes, width=16) -> str:
        lines = []
        for offset in range(0, len(data), width):
            chunk = data[offset:offset + width]
            hex_part = " ".join(f"{b:02X}" for b in chunk).ljust(width * 3)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            lines.append(f"{offset:08X}:  {hex_part}  {ascii_part}")
        return "\n".join(lines)

    def prevent_offset_edit(self, event=None):
        try:
            index = self.index(tk.CURRENT)
            line, col = map(int, index.split('.'))
            if col < 9:
                self.mark_set(tk.INSERT, f"{line}.9")
                return "break"
        except Exception:
            pass

    def on_edit(self, event=None):
        try:
            content = self.get("1.0", tk.END).rstrip('\n').splitlines()
            new_data = bytearray()
            for line in content:
                parts = line.split(":", 1)
                if len(parts) < 2:
                    continue
                rest = parts[1].strip()
                if "  " not in rest:
                    continue
                hex_str, _ = rest.split("  ", 1)
                hex_bytes = []
                for h in hex_str.split():
                    try:
                        hex_bytes.append(int(h, 16))
                    except ValueError:
                        hex_bytes.append(0x2E)
                new_data.extend(hex_bytes)
            self.data = new_data
            self.delete("1.0", tk.END)
            self.insert("1.0", self.format_hex(self.data))
            if self.on_change:
                try:
                    self.on_change(bytes(self.data))
                except Exception:
                    pass
        except Exception as e:
            print("HexEditor parse error:", e)

    def get_bytes(self) -> bytes:
        return bytes(self.data)

def safe_convert(obj):
    if isinstance(obj, (bytes, bytearray)):
        b = bytes(obj)
        return {'_type': 'bytes', 'length': len(b), 'hex': b.hex(), 'ascii': ''.join(chr(x) if 32 <= x < 127 else '.' for x in b[:256])}
    if isinstance(obj, dict):
        return {k: safe_convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_convert(x) for x in obj]
    return obj

class NCSReaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('NCS Reader - Fixed')
        self.geometry('1280x820')
        self.configure(bg='#1e1e1e')
        self.files = {}
        self.current = None

        self.create_toolbar()
        self.create_main_panes()

    def create_toolbar(self):
        bar = tk.Frame(self, bg='#2b2b2b')
        bar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(bar, text='Open File', command=self.open_file).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(bar, text='Open Folder', command=self.open_folder).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(bar, text='Save JSON', command=self.save_json).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(bar, text='Save Edited NCS', command=self.save_ncs).pack(side=tk.LEFT, padx=6, pady=6)

    def create_main_panes(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg='#1e1e1e')
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        left = tk.Frame(paned, bg='#252526')
        self.file_list = tk.Listbox(left, bg='#252526', fg='white', selectbackground='#007acc', width=40)
        self.file_list.pack(fill=tk.BOTH, expand=True)
        self.file_list.bind('<<ListboxSelect>>', self.on_select)
        paned.add(left, width=300)

        notebook_frame = ttk.Frame(paned)
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        paned.add(notebook_frame)
        try:
            paned.paneconfigure(notebook_frame, stretch="always")
        except Exception:
            pass

        json_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.json_text = tk.Text(json_tab, wrap='none', bg='#1e1e1e', fg='white', insertbackground='white', font=('Courier New',10))
        self.json_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        json_scroll = ttk.Scrollbar(json_tab, command=self.json_text.yview)
        json_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_text.config(yscrollcommand=json_scroll.set)
        self.notebook.add(json_tab, text='JSON View')

        table_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        cols = ('Offset','Length','ASCII','HexPreview','Ints','Floats','Guessed')
        self.table = ttk.Treeview(table_tab, columns=cols, show='headings')
        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, width=140 if c!='HexPreview' else 260, anchor='w')
        self.table.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        table_scroll = ttk.Scrollbar(table_tab, command=self.table.yview)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.config(yscrollcommand=table_scroll.set)
        self.notebook.add(table_tab, text='Detailed Table')

        hex_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.hex_editor = HexEditor(hex_tab, b'', on_change=self.on_hex_change, bg='#1e1e1e', fg='white', insertbackground='white')
        self.hex_editor.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        hex_scroll = ttk.Scrollbar(hex_tab, command=self.hex_editor.yview)
        hex_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.hex_editor.config(yscrollcommand=hex_scroll.set)
        self.notebook.add(hex_tab, text='Hex Editor')

    def open_file(self):
        p = filedialog.askopenfilename(filetypes=[('NCS files','*.ncs'),('All files','*.*')])
        if p:
            name = os.path.basename(p)
            self.files[name] = p
            if name not in self.file_list.get(0, tk.END):
                self.file_list.insert(tk.END, name)

    def open_folder(self):
        d = filedialog.askdirectory()
        if d:
            found = [os.path.join(d,f) for f in os.listdir(d) if f.lower().endswith('.ncs')]
            for f in found:
                name = os.path.basename(f)
                self.files[name] = f
                if name not in self.file_list.get(0, tk.END):
                    self.file_list.insert(tk.END, name)

    def on_select(self, event):
        sel = self.file_list.curselection()
        if not sel:
            return
        name = self.file_list.get(sel[0])
        path = self.files.get(name)
        if path:
            self.load_file(name, path)

    def load_file(self, name, path):
        parser = get_parser_for(path)
        parsed = parser.parse(path)
        self.current = (name, path, parsed, parser)

        safe = safe_convert(parsed.get('structured', {}))
        self.json_text.delete('1.0', tk.END)
        self.json_text.insert('1.0', json.dumps(safe, indent=4, ensure_ascii=False))

        self.table.delete(*self.table.get_children())
        for rec in parsed.get('structured', {}).get('records', []):
            offset = rec.get('offset', ''); length = rec.get('length', '')
            ascii_txt = (rec.get('ascii_text') or '')[:80].replace('\n',' ')
            hex_preview = (rec.get('raw_hex') or '')[:192]
            ints = ','.join(str(x) for x in (rec.get('int32_values') or [])[:6])
            floats = ','.join(str(x) for x in (rec.get('float32_values') or [])[:6])
            guessed = rec.get('guessed', '') or ''
            self.table.insert('', 'end', values=(offset, length, ascii_txt, hex_preview, ints, floats, guessed))

        raw = parsed.get('raw') or parsed.get('raw_bytes') or b''
        self.hex_editor.delete('1.0', tk.END)
        self.hex_editor.data = bytearray(raw)
        self.hex_editor.insert('1.0', self.hex_editor.format_hex(raw))

    def on_hex_change(self, data: bytes):
        if not self.current:
            return
        name, path, parsed, parser = self.current
        try:
            if hasattr(parser, 'parse_bytes'):
                new_parsed = parser.parse_bytes(data)
            else:
                import tempfile
                tf = tempfile.NamedTemporaryFile(delete=False)
                tf.write(data); tf.close()
                new_parsed = parser.parse(tf.name)
                os.unlink(tf.name)
            self.current = (name, path, new_parsed, parser)
            safe = safe_convert(new_parsed.get('structured', {}))
            self.json_text.delete('1.0', tk.END)
            self.json_text.insert('1.0', json.dumps(safe, indent=4, ensure_ascii=False))

            self.table.delete(*self.table.get_children())
            for rec in new_parsed.get('structured', {}).get('records', []):
                offset = rec.get('offset', ''); length = rec.get('length', '')
                ascii_txt = (rec.get('ascii_text') or '')[:80].replace('\n',' ')
                hex_preview = (rec.get('raw_hex') or '')[:192]
                ints = ','.join(str(x) for x in (rec.get('int32_values') or [])[:6])
                floats = ','.join(str(x) for x in (rec.get('float32_values') or [])[:6])
                guessed = rec.get('guessed', '') or ''
                self.table.insert('', 'end', values=(offset, length, ascii_txt, hex_preview, ints, floats, guessed))
        except Exception as e:
            print('Error re-parsing bytes:', e)

    def save_json(self):
        if not self.current:
            messagebox.showwarning('No file', 'No file selected')
            return
        name, path, parsed, parser = self.current
        p = filedialog.asksaveasfilename(defaultextension='.json', initialfile=f'Edited_{name}.json')
        if not p: return
        safe = safe_convert(parsed.get('structured', {}))
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(safe, f, indent=4, ensure_ascii=False)
        messagebox.showinfo('Saved', f'JSON exported to {p}')

    def save_ncs(self):
        if not self.current:
            messagebox.showwarning('No file', 'No file selected')
            return
        name, path, parsed, parser = self.current
        savep = filedialog.asksaveasfilename(defaultextension='.ncs', initialfile=f'Edited_{name}')
        if not savep: return
        raw = self.hex_editor.get_bytes()
        try:
            with open(savep, 'wb') as f:
                f.write(raw)
            messagebox.showinfo('Saved', f'Edited NCS written to {savep}')
        except Exception as e:
            messagebox.showerror('Save error', str(e))

def main():
    app = NCSReaderApp()
    app.mainloop()

if __name__ == '__main__':
    main()
