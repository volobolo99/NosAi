"""NosAi Launcher/Scanner - GUI Windows senza dipendenze esterne."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class NosAiLauncher(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("NosAi — Launcher / Scanner")
        self.geometry("900x620")
        self.minsize(760, 520)
        self.configure(bg="#111827")
        self.client_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Seleziona la cartella del client NosTale")
        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#ffffff")
        style.configure("Status.TLabel", font=("Segoe UI", 11, "bold"), foreground="#93c5fd")

        root = tk.Frame(self, bg="#111827", padx=28, pady=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="NosAi", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Launcher / Scanner del client NosTale").pack(anchor="w", pady=(2, 22))

        card = tk.Frame(root, bg="#1f2937", padx=20, pady=20)
        card.pack(fill="x")
        ttk.Label(card, text="Cartella client NosTale").pack(anchor="w")
        row = tk.Frame(card, bg="#1f2937")
        row.pack(fill="x", pady=(8, 12))
        entry = tk.Entry(row, textvariable=self.client_var, font=("Segoe UI", 11), bg="#374151", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=9)
        ttk.Button(row, text="Seleziona cartella", command=self.select_folder).pack(side="left", padx=(10, 0))
        self.scan_button = ttk.Button(card, text="▶  Avvia analisi", command=self.start_scan)
        self.scan_button.pack(anchor="w")

        ttk.Label(root, textvariable=self.status_var, style="Status.TLabel").pack(anchor="w", pady=(18, 8))
        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 12))

        ttk.Label(root, text="Risultato analisi").pack(anchor="w")
        self.output = tk.Text(root, height=18, bg="#0b1220", fg="#d1d5db", insertbackground="#ffffff", relief="flat", font=("Consolas", 9))
        self.output.pack(fill="both", expand=True, pady=(6, 0))

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleziona la cartella del client NosTale")
        if folder:
            self.client_var.set(folder)
            self.status_var.set("Cartella selezionata — pronto per l'analisi")

    def start_scan(self) -> None:
        client = self.client_var.get().strip()
        if not client or not Path(client).is_dir():
            messagebox.showwarning("NosAi", "Seleziona prima una cartella NosTale valida.")
            return
        self.scan_button.configure(state="disabled")
        self.progress.start(12)
        self.output.delete("1.0", "end")
        self.status_var.set("Analisi del client in corso…")
        threading.Thread(target=self._run_scan, args=(client,), daemon=True).start()

    def _run_scan(self, client: str) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "e2e_client_scan.py"
        manifest = Path(__file__).resolve().parents[1] / "artifacts" / "client-manifest.json"
        command = [sys.executable, str(script), client, "--manifest", str(manifest)]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
            text = result.stdout + ("\n\nERRORI:\n" + result.stderr if result.stderr else "")
            self.after(0, self._scan_finished, result.returncode, text)
        except Exception as exc:
            self.after(0, self._scan_finished, 1, f"Errore durante l'analisi: {exc}")

    def _scan_finished(self, code: int, text: str) -> None:
        self.progress.stop()
        self.scan_button.configure(state="normal")
        self.output.insert("1.0", text)
        self.status_var.set("Analisi completata: OK" if code == 0 else "Analisi completata: prerequisiti mancanti o errore")


def main() -> int:
    NosAiLauncher().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
