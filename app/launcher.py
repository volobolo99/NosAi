"""Nos AI Launcher Test - Windows GUI for exhaustive local client diagnostics."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class NosAiLauncherTest(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Nos AI Launcher Test")
        self.geometry("1080x760")
        self.minsize(900, 650)
        self.configure(bg="#0b1020")
        self.client_var = tk.StringVar()
        self.status_var = tk.StringVar(value="1. Seleziona la cartella del client NosTale")
        self.percent_var = tk.StringVar(value="0%")
        self.detail_var = tk.StringVar(value="In attesa")
        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("TLabel", background="#0b1020", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"), foreground="#ffffff")
        style.configure("Sub.TLabel", font=("Segoe UI", 11), foreground="#9ca3af")
        style.configure("Step.TLabel", font=("Segoe UI", 10, "bold"), foreground="#dbeafe")

        root = tk.Frame(self, bg="#0b1020", padx=30, pady=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Nos AI Launcher Test", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Raccolta diagnostica completa del client NosTale per lo sviluppo di NosAi", style="Sub.TLabel").pack(anchor="w", pady=(3, 22))

        card = tk.Frame(root, bg="#151d33", padx=20, pady=18)
        card.pack(fill="x")
        ttk.Label(card, text="Client NosTale", style="Step.TLabel").pack(anchor="w")
        row = tk.Frame(card, bg="#151d33")
        row.pack(fill="x", pady=(8, 12))
        entry = tk.Entry(row, textvariable=self.client_var, font=("Segoe UI", 11), bg="#222d49", fg="#fff", insertbackground="#fff", relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=10)
        ttk.Button(row, text="Seleziona cartella", command=self.select_folder).pack(side="left", padx=(10, 0))
        self.start_button = ttk.Button(card, text="▶  AVVIA TEST COMPLETO", command=self.start_scan)
        self.start_button.pack(anchor="w")

        progress_card = tk.Frame(root, bg="#151d33", padx=20, pady=18)
        progress_card.pack(fill="x", pady=16)
        top = tk.Frame(progress_card, bg="#151d33")
        top.pack(fill="x")
        ttk.Label(top, textvariable=self.status_var, style="Step.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.percent_var, style="Step.TLabel").pack(side="right")
        self.progress = ttk.Progressbar(progress_card, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(12, 8))
        ttk.Label(progress_card, textvariable=self.detail_var).pack(anchor="w")

        ttk.Label(root, text="Fasi del test", style="Step.TLabel").pack(anchor="w")
        self.steps = tk.Listbox(root, height=8, bg="#10182a", fg="#cbd5e1", selectbackground="#1d4ed8", relief="flat", font=("Segoe UI", 10))
        self.steps.pack(fill="x", pady=(6, 14))
        for step in (
            "01  Verifica struttura client e NostaleData",
            "02  Inventario file .NOS e famiglie asset",
            "03  Hash SHA-256 e metadati",
            "04  Analisi NSpn / NSpc / NSpm / sprite / texture",
            "05  Analisi effetti, geometria e risorse correlate",
            "06  Raccolta ambiente Windows e compatibilità",
            "07  Generazione report diagnostico e manifest",
            "08  Preparazione pacchetto da caricare su GitHub",
        ):
            self.steps.insert("end", "○  " + step)

        ttk.Label(root, text="Log diagnostico", style="Step.TLabel").pack(anchor="w")
        self.output = tk.Text(root, height=13, bg="#070c17", fg="#cbd5e1", insertbackground="#fff", relief="flat", font=("Consolas", 9))
        self.output.pack(fill="both", expand=True, pady=(6, 0))

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleziona la cartella principale del client NosTale")
        if folder:
            self.client_var.set(folder)
            self.status_var.set("Pronto: avvia il test completo")
            self.detail_var.set("Cartella selezionata")

    def start_scan(self) -> None:
        client = self.client_var.get().strip()
        if not client or not Path(client).is_dir():
            messagebox.showwarning("Nos AI Launcher Test", "Seleziona prima la cartella principale del client NosTale.")
            return
        self.start_button.configure(state="disabled")
        self.progress.configure(value=5)
        self.percent_var.set("5%")
        self.output.delete("1.0", "end")
        self.detail_var.set("Preparazione raccolta dati…")
        threading.Thread(target=self._run_scan, args=(client,), daemon=True).start()

    def _run_scan(self, client: str) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "e2e_client_scan.py"
        root = Path(__file__).resolve().parents[1]
        artifacts = root / "artifacts"
        artifacts.mkdir(exist_ok=True)
        manifest = artifacts / "client-manifest.json"
        report = artifacts / "nosai-client-test-report.json"
        command = [sys.executable, str(script), client, "--manifest", str(manifest), "--report", str(report), "--full"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
            text = result.stdout + ("\n\nERRORI:\n" + result.stderr if result.stderr else "")
            self.after(0, self._scan_finished, result.returncode, text, report)
        except Exception as exc:
            self.after(0, self._scan_finished, 1, f"Errore durante il test: {exc}", report)

    def _scan_finished(self, code: int, text: str, report: Path) -> None:
        self.progress.configure(value=100 if code == 0 else 95)
        self.percent_var.set("100%" if code == 0 else "95%")
        self.output.insert("1.0", text)
        self.start_button.configure(state="normal")
        if code == 0:
            self.status_var.set("TEST COMPLETATO — dati raccolti")
            self.detail_var.set(f"Report locale: {report}")
            for i in range(self.steps.size()):
                self.steps.itemconfig(i, foreground="#86efac")
        else:
            self.status_var.set("TEST COMPLETATO CON PROBLEMI — controlla il log")
            self.detail_var.set("Il report è stato comunque salvato per la diagnosi")


def main() -> int:
    NosAiLauncherTest().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
