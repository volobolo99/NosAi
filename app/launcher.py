"""Nos AI Launcher Test: guided, read-only NosTale diagnostics for Windows."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import threading
import time
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.diagnostics.collector import collect_diagnostics, write_report
from app.diagnostics.sanitize import sanitize_report


RELEVANT_EXTENSIONS = {
    ".nos", ".exe", ".dll", ".dat", ".pak", ".idx", ".ini", ".json",
    ".png", ".jpg", ".jpeg", ".bmp", ".tga", ".dds", ".spr", ".anm", ".anim",
}
MAX_HASH_BYTES = 512 * 1024 * 1024


class NosAiLauncherTest(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Nos AI Launcher Test")
        self.geometry("1100x780")
        self.minsize(900, 650)
        self.configure(bg="#0b1020")
        self.client_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Seleziona la cartella principale di NosTale")
        self.detail_var = tk.StringVar(value="In attesa")
        self.percent_var = tk.StringVar(value="0%")
        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("TLabel", background="#0b1020", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0b1020", foreground="#ffffff", font=("Segoe UI", 25, "bold"))
        style.configure("Sub.TLabel", background="#0b1020", foreground="#9ca3af", font=("Segoe UI", 11))
        style.configure("Step.TLabel", background="#151d33", foreground="#dbeafe", font=("Segoe UI", 10, "bold"))

        root = tk.Frame(self, bg="#0b1020", padx=30, pady=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Nos AI Launcher Test", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Raccolta diagnostica completa e non invasiva del client NosTale", style="Sub.TLabel").pack(anchor="w", pady=(3, 20))

        card = tk.Frame(root, bg="#151d33", padx=20, pady=18)
        card.pack(fill="x")
        ttk.Label(card, text="1. Cartella client NosTale", style="Step.TLabel").pack(anchor="w")
        row = tk.Frame(card, bg="#151d33")
        row.pack(fill="x", pady=(8, 12))
        entry = tk.Entry(row, textvariable=self.client_var, font=("Segoe UI", 11), bg="#222d49", fg="#fff", insertbackground="#fff", relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=10)
        ttk.Button(row, text="Seleziona cartella", command=self.select_folder).pack(side="left", padx=(10, 0))
        self.start_button = ttk.Button(card, text="▶  AVVIA TEST COMPLETO", command=self.start_test)
        self.start_button.pack(anchor="w")

        progress = tk.Frame(root, bg="#151d33", padx=20, pady=18)
        progress.pack(fill="x", pady=16)
        top = tk.Frame(progress, bg="#151d33")
        top.pack(fill="x")
        ttk.Label(top, textvariable=self.status_var, style="Step.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.percent_var, style="Step.TLabel").pack(side="right")
        self.bar = ttk.Progressbar(progress, maximum=100, mode="determinate")
        self.bar.pack(fill="x", pady=(12, 8))
        ttk.Label(progress, textvariable=self.detail_var).pack(anchor="w")

        ttk.Label(root, text="2. Fasi", background="#0b1020", foreground="#dbeafe", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.steps = tk.Listbox(root, height=8, bg="#10182a", fg="#cbd5e1", relief="flat", font=("Segoe UI", 10))
        self.steps.pack(fill="x", pady=(6, 14))
        for text in (
            "Verifica struttura e identifica la cartella del client",
            "Inventario file e famiglie di risorse",
            "Raccolta metadati e SHA-256 delle risorse rilevanti",
            "Raccolta Windows, CPU, GPU, RAM e runtime",
            "Rilevamento osservativo del client NosTale in esecuzione",
            "Generazione manifest e report diagnostico",
            "Sanitizzazione del report condivisibile",
            "Creazione pacchetto ZIP diagnostico",
        ):
            self.steps.insert("end", "○  " + text)

        ttk.Label(root, text="3. Log", background="#0b1020", foreground="#dbeafe", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.log = tk.Text(root, height=12, bg="#070c17", fg="#cbd5e1", relief="flat", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(6, 0))

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleziona la cartella principale del client NosTale")
        if folder:
            self.client_var.set(folder)
            self.status_var.set("Pronto per il test")
            self.detail_var.set("Cartella selezionata")

    def _set_step(self, index: int, state: str) -> None:
        symbols = {"done": "✓", "active": "●", "pending": "○"}
        original = self.steps.get(index).lstrip("○✓● ")
        self.steps.delete(index)
        self.steps.insert(index, f"{symbols[state]}  {original}")
        self.steps.itemconfig(index, foreground="#86efac" if state == "done" else "#93c5fd")

    def _progress(self, value: int, status: str, detail: str) -> None:
        self.bar["value"] = value
        self.percent_var.set(f"{value}%")
        self.status_var.set(status)
        self.detail_var.set(detail)

    def _append(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def start_test(self) -> None:
        client = Path(self.client_var.get().strip()).expanduser()
        if not client.is_dir():
            messagebox.showwarning("Nos AI Launcher Test", "Seleziona una cartella NosTale valida.")
            return
        self.start_button.configure(state="disabled")
        self.log.delete("1.0", "end")
        for i in range(self.steps.size()):
            self.steps.itemconfig(i, foreground="#cbd5e1")
        threading.Thread(target=self._run_test, args=(client.resolve(),), daemon=True).start()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _run_test(self, client: Path) -> None:
        root = Path.cwd() / "artifacts"
        root.mkdir(parents=True, exist_ok=True)
        report_path = root / "nosai-client-test-report.json"
        safe_report = root / "nosai-client-test-report.sanitized.json"
        manifest_path = root / "client-manifest.json"
        package_path = root / "nosai-diagnostic-package.zip"
        try:
            self.after(0, self._progress, 5, "Fase 1/8 — verifica client", str(client))
            self.after(0, self._set_step, 0, "active")
            children = list(client.iterdir())
            self.after(0, self._set_step, 0, "done")
            self.after(0, self._append, f"Cartella valida: {client}")
            self.after(0, self._append, f"Elementi immediati: {len(children)}")

            self.after(0, self._progress, 15, "Fase 2/8 — inventario risorse", "Scansione ricorsiva…")
            self.after(0, self._set_step, 1, "active")
            files = []
            for path in client.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    continue
                rel = path.relative_to(client).as_posix()
                files.append({"path": rel, "size": stat.st_size, "suffix": path.suffix.lower()})
            self.after(0, self._set_step, 1, "done")
            self.after(0, self._append, f"File trovati: {len(files)}")

            self.after(0, self._progress, 35, "Fase 3/8 — hash e famiglie", "Analisi delle risorse rilevanti…")
            self.after(0, self._set_step, 2, "active")
            relevant = [item for item in files if item["suffix"] in RELEVANT_EXTENSIONS]
            for number, item in enumerate(relevant, 1):
                if item["size"] <= MAX_HASH_BYTES:
                    try:
                        item["sha256"] = self._sha256(client / item["path"])
                    except OSError as exc:
                        item["hash_error"] = type(exc).__name__
                else:
                    item["hash_skipped"] = "file_too_large"
                if number % max(1, len(relevant) // 20 or 1) == 0:
                    pct = 35 + int(number / max(1, len(relevant)) * 20)
                    self.after(0, self._progress, min(55, pct), "Fase 3/8 — hash e famiglie", f"{number}/{len(relevant)} risorse")
            self.after(0, self._set_step, 2, "done")

            self.after(0, self._progress, 60, "Fase 4/8 — ambiente Windows", "Raccolta hardware e runtime…")
            self.after(0, self._set_step, 3, "active")
            diagnostics = collect_diagnostics()
            self.after(0, self._set_step, 3, "done")
            self.after(0, self._append, "Diagnostica Windows completata")

            self.after(0, self._progress, 70, "Fase 5/8 — client reale", "Controllo osservativo del processo…")
            self.after(0, self._set_step, 4, "active")
            connected = bool(diagnostics.get("nostale", {}).get("connected"))
            self.after(0, self._append, f"NosTale rilevato: {'SÌ' if connected else 'NO'}")
            self.after(0, self._set_step, 4, "done")

            families: dict[str, int] = {}
            for item in relevant:
                suffix = item["suffix"] or "<nessuna>"
                families[suffix] = families.get(suffix, 0) + 1
            manifest = {
                "schema": "nosai.client-manifest.v2",
                "created_unix": time.time(),
                "client_root": str(client),
                "file_count": len(files),
                "relevant_file_count": len(relevant),
                "families": dict(sorted(families.items())),
                "files": relevant,
            }
            report = {
                "schema": "nosai.client-test.v2",
                "collector": {"launcher": "Nos AI Launcher Test", "version": "2.0"},
                "client": {"root": str(client), "file_count": len(files), "relevant_file_count": len(relevant)},
                "manifest": manifest,
                "diagnostics": diagnostics,
            }
            self.after(0, self._progress, 82, "Fase 6/8 — report", "Scrittura manifest e report…")
            self.after(0, self._set_step, 5, "active")
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            write_report(report_path, report)
            self.after(0, self._set_step, 5, "done")

            self.after(0, self._progress, 90, "Fase 7/8 — privacy", "Sanitizzazione del report…")
            self.after(0, self._set_step, 6, "active")
            sanitize_report(report_path, safe_report)
            self.after(0, self._set_step, 6, "done")

            self.after(0, self._progress, 96, "Fase 8/8 — pacchetto", "Creazione ZIP…")
            self.after(0, self._set_step, 7, "active")
            with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(safe_report, safe_report.name)
                archive.write(manifest_path, manifest_path.name)
                archive.writestr("PACKAGE_VERSION.txt", "NosAi diagnostic package v2\n")
            self.after(0, self._set_step, 7, "done")
            self.after(0, self._progress, 100, "TEST COMPLETATO", f"Pacchetto: {package_path}")
            self.after(0, self._append, "=== RISULTATO ===")
            self.after(0, self._append, f"Report: {report_path}")
            self.after(0, self._append, f"Report sanitizzato: {safe_report}")
            self.after(0, self._append, f"Manifest: {manifest_path}")
            self.after(0, self._append, f"Pacchetto: {package_path}")
        except Exception as exc:
            self.after(0, self._progress, 100, "TEST TERMINATO CON ERRORE", f"{type(exc).__name__}: {exc}")
            self.after(0, self._append, f"ERRORE: {type(exc).__name__}: {exc}")
        finally:
            self.after(0, self.start_button.configure, {"state": "normal"})


def main() -> int:
    NosAiLauncherTest().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
