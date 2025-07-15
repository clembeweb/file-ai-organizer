
import threading, json, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from organizer import scan_directory, apply_actions, DEFAULT_RULES

class FileAIOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File AI Organizer")
        self.geometry("900x600")
        self.actions = []
        self._create_widgets()

    def _create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # Dashboard Tab
        dash_frame = ttk.Frame(notebook)
        notebook.add(dash_frame, text="Dashboard")
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(dash_frame, textvariable=self.path_var, width=70)
        path_entry.grid(column=0, row=0, padx=10, pady=10, sticky='w')
        ttk.Button(dash_frame, text="Sfoglia...", command=self.browse_dir).grid(column=1,row=0,padx=5)
        ttk.Button(dash_frame, text="Scansiona", command=self.start_scan).grid(column=2,row=0,padx=5)

        stats_frame = ttk.Frame(dash_frame)
        stats_frame.grid(column=0,row=1,columnspan=3,pady=10,sticky='w')
        self.stats_label = ttk.Label(stats_frame, text="Nessuna scansione eseguita.")
        self.stats_label.pack(anchor='w')

        # Review Tab
        review_frame = ttk.Frame(notebook)
        notebook.add(review_frame, text="Revisione")
        cols = ("Action","Target","Destination/DuplicateOf")
        self.tree = ttk.Treeview(review_frame, columns=cols, show='headings', height=20)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=250 if c!="Action" else 100, anchor='w')
        self.tree.pack(fill='both', expand=True, side='left', padx=(10,0), pady=10)
        scrollbar = ttk.Scrollbar(review_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y', pady=10)

        btn_frame = ttk.Frame(review_frame)
        btn_frame.pack(fill='x', padx=10, pady=(0,10))
        ttk.Button(btn_frame, text="Applica azioni", command=self.apply_selected).pack(side='left')
        ttk.Button(btn_frame, text="Aggiorna lista", command=self.refresh_review_tab).pack(side='left', padx=5)

        # Settings Tab (simple)
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Impostazioni")
        ttk.Label(settings_frame, text="Estensioni da eliminare (separate da virgola):").grid(row=0,column=0,sticky='w',padx=10,pady=5)
        self.ext_var = tk.StringVar(value=", ".join(DEFAULT_RULES['delete_extensions']))
        ttk.Entry(settings_frame, textvariable=self.ext_var, width=40).grid(row=0,column=1, padx=10, pady=5, sticky='w')
        ttk.Label(settings_frame, text="Elimina dopo N giorni:").grid(row=1,column=0,sticky='w',padx=10,pady=5)
        self.days_var = tk.IntVar(value=DEFAULT_RULES['delete_older_than_days'])
        ttk.Entry(settings_frame, textvariable=self.days_var, width=10).grid(row=1,column=1, padx=10, pady=5, sticky='w')

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)

    def start_scan(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Percorso mancante", "Seleziona una cartella da scansionare.")
            return
        # update rules from settings
        exts = [e.strip() if e.strip().startswith('.') else '.'+e.strip() for e in self.ext_var.get().split(',') if e.strip()]
        DEFAULT_RULES['delete_extensions'] = exts
        DEFAULT_RULES['delete_older_than_days'] = max(1, self.days_var.get())

        threading.Thread(target=self._scan_thread, args=(path,), daemon=True).start()
        self.stats_label.config(text="Scansione in corso...")

    def _scan_thread(self, path):
        try:
            actions = scan_directory(path, DEFAULT_RULES)
            self.actions = actions
            duplicates = sum(1 for a in actions if a['action'] == 'delete_duplicate')
            temps = sum(1 for a in actions if a['action'] == 'delete_temp')
            moves = sum(1 for a in actions if a['action'] == 'move_to_extension_folder')
            self.after(0, lambda: self._scan_complete(len(actions), duplicates, temps, moves))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Errore scansione", str(e)))

    def _scan_complete(self, total, dup, temp, moves):
        self.stats_label.config(text=f"Azioni proposte: {total}  | Duplicati: {dup}  | Temp: {temp}  | Spostamenti: {moves}")
        self.refresh_review_tab()

    def refresh_review_tab(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for act in self.actions:
            dest = act.get('destination') or act.get('duplicate_of') or ''
            self.tree.insert('', 'end', values=(act['action'], act['target'], dest))

    def apply_selected(self):
        if not self.actions:
            messagebox.showinfo("Nessuna azione", "Nessuna azione da applicare.")
            return
        if not messagebox.askyesno("Conferma", "Applicare tutte le azioni elencate?"):
            return
        summary = apply_actions(self.actions)
        messagebox.showinfo("Completato", f"Eliminati: {summary['deleted']}, Spostati: {summary['moved']}, Errori: {summary['errors']}")
        self.actions=[]
        self.refresh_review_tab()
        self.stats_label.config(text="Operazioni completate.")

if __name__ == "__main__":
    app = FileAIOrganizerApp()
    app.mainloop()
