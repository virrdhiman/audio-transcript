"""
Audio Transcript App
--------------------
Browse for one or more audio/call recordings, generate a word-by-word
transcript with timestamps, and save a Microsoft Word (.docx) file that
includes the call recording time.
"""

from __future__ import annotations

import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from transcriber import (
    download_model,
    format_duration,
    format_timestamp,
    transcribe_audio,
)
from word_export import export_to_word

AUDIO_EXTENSIONS = (
    "*.wav *.mp3 *.m4a *.mp4 *.mpeg *.mpga *.webm *.ogg *.flac *.wma *.aac"
)

MODEL_CHOICES = ("tiny", "base", "small", "medium", "large-v3")


class TranscriptApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Audio Transcript → Word")
        self.geometry("780x560")
        self.minsize(680, 480)

        self.files: list[Path] = []
        self.output_dir = tk.StringVar(value=str(Path.home() / "Documents"))
        self.model_size = tk.StringVar(value="base")
        self.status = tk.StringVar(value="Add audio files to begin.")
        self._busy = False

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        header = ttk.Label(
            self,
            text="Call / Audio Transcript Generator",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(anchor="w", **pad)

        hint = ttk.Label(
            self,
            text=(
                "Select one or more recordings. Each file becomes a Word document "
                "with call recording time and a word-by-word timestamped transcript."
            ),
            wraplength=740,
        )
        hint.pack(anchor="w", padx=10)

        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", **pad)
        ttk.Button(btn_row, text="Browse files…", command=self.add_files).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_row, text="Clear list", command=self.clear_files).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(
            btn_row, text="Choose output folder…", command=self.choose_output
        ).pack(side="left")

        list_frame = ttk.LabelFrame(self, text="Selected audio files")
        list_frame.pack(fill="both", expand=True, **pad)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)

        opts = ttk.Frame(self)
        opts.pack(fill="x", **pad)
        ttk.Label(opts, text="Whisper model:").pack(side="left")
        ttk.Combobox(
            opts,
            textvariable=self.model_size,
            values=MODEL_CHOICES,
            state="readonly",
            width=12,
        ).pack(side="left", padx=8)
        self.download_btn = ttk.Button(
            opts, text="Download model", command=self.start_download_model
        )
        self.download_btn.pack(side="left", padx=(4, 8))
        ttk.Label(
            opts,
            text="(base = good balance; download before first transcript)",
        ).pack(side="left")

        out_row = ttk.Frame(self)
        out_row.pack(fill="x", **pad)
        ttk.Label(out_row, text="Output folder:").pack(side="left")
        ttk.Entry(out_row, textvariable=self.output_dir).pack(
            side="left", fill="x", expand=True, padx=8
        )

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=(0, 4))

        self.log = tk.Text(self, height=8, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=False, padx=10, pady=4)

        action = ttk.Frame(self)
        action.pack(fill="x", **pad)
        self.run_btn = ttk.Button(
            action, text="Generate Word transcripts", command=self.start_transcription
        )
        self.run_btn.pack(side="left")
        ttk.Label(action, textvariable=self.status).pack(side="left", padx=12)

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select audio / call recordings",
            filetypes=[
                ("Audio files", AUDIO_EXTENSIONS),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return
        for raw in paths:
            path = Path(raw)
            if path not in self.files:
                self.files.append(path)
                self.listbox.insert(tk.END, str(path))
        self.status.set(f"{len(self.files)} file(s) selected.")

    def clear_files(self) -> None:
        self.files.clear()
        self.listbox.delete(0, tk.END)
        self.status.set("File list cleared.")

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_dir.set(folder)

    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.run_btn.configure(state=state)
        self.download_btn.configure(state=state)

    def start_download_model(self) -> None:
        if self._busy:
            return
        model = self.model_size.get()
        self._set_busy(True)
        self.progress.configure(mode="indeterminate")
        self.progress.start(12)
        self.status.set(f"Downloading model '{model}'…")
        self._append_log(f"Downloading Whisper model '{model}' (internet required)…")

        thread = threading.Thread(
            target=self._download_worker,
            args=(model,),
            daemon=True,
        )
        thread.start()

    def _download_worker(self, model: str) -> None:
        try:
            message = download_model(model_size=model)
            self.after(0, lambda: self._download_done(success=True, message=message))
        except Exception as exc:  # noqa: BLE001 - show in UI
            err = f"Model download failed: {exc}"
            self.after(0, lambda: self._append_log(err))
            self.after(0, lambda: self._append_log(traceback.format_exc()))
            self.after(0, lambda: self._download_done(success=False, message=err))

    def _download_done(self, success: bool, message: str) -> None:
        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)
        self._set_busy(False)
        self._append_log(message)
        if success:
            self.status.set(message)
            messagebox.showinfo("Model ready", message)
        else:
            self.status.set("Model download failed.")
            messagebox.showerror(
                "Download failed",
                f"{message}\n\nCheck your internet connection and try again.",
            )

    def start_transcription(self) -> None:
        if self._busy:
            return
        if not self.files:
            messagebox.showwarning("No files", "Please browse and add at least one audio file.")
            return
        out_dir = Path(self.output_dir.get().strip() or ".")
        out_dir.mkdir(parents=True, exist_ok=True)

        self._set_busy(True)
        self.progress.configure(mode="determinate", maximum=len(self.files), value=0)
        self.status.set("Working…")
        self._append_log("Starting transcription…")

        files = list(self.files)
        model = self.model_size.get()

        thread = threading.Thread(
            target=self._worker,
            args=(files, out_dir, model),
            daemon=True,
        )
        thread.start()

    def _worker(self, files: list[Path], out_dir: Path, model: str) -> None:
        errors: list[str] = []
        created: list[Path] = []
        try:
            for index, audio in enumerate(files, start=1):
                self.after(
                    0,
                    lambda a=audio, i=index: self._append_log(
                        f"[{i}/{len(files)}] Transcribing: {a.name}"
                    ),
                )
                try:
                    result = transcribe_audio(audio, model_size=model)
                    doc_path = out_dir / f"{audio.stem}_transcript.docx"
                    export_to_word(result, doc_path, source_name=audio.name)
                    created.append(doc_path)
                    summary = (
                        f"  → Saved {doc_path.name} | "
                        f"recording time {format_duration(result.duration_seconds)} "
                        f"({format_timestamp(result.duration_seconds)}) | "
                        f"{len(result.words)} words"
                    )
                    self.after(0, lambda s=summary: self._append_log(s))
                except Exception as exc:  # noqa: BLE001 - show in UI
                    msg = f"Failed on {audio.name}: {exc}"
                    errors.append(msg)
                    self.after(0, lambda m=msg: self._append_log(m))
                    self.after(0, lambda: self._append_log(traceback.format_exc()))
                finally:
                    self.after(0, lambda v=index: self.progress.configure(value=v))
        finally:
            self.after(0, lambda: self._done(created, errors))

    def _done(self, created: list[Path], errors: list[str]) -> None:
        self._set_busy(False)
        if created and not errors:
            self.status.set(f"Done. Created {len(created)} Word file(s).")
            messagebox.showinfo(
                "Complete",
                f"Created {len(created)} Word transcript(s) in:\n{self.output_dir.get()}",
            )
        elif created and errors:
            self.status.set(f"Finished with {len(errors)} error(s).")
            messagebox.showwarning(
                "Partial success",
                f"Created {len(created)} file(s), but {len(errors)} failed.\n"
                "See the log for details.",
            )
        else:
            self.status.set("All files failed.")
            messagebox.showerror(
                "Failed",
                "Could not create transcripts.\nSee the log for details.",
            )


def main() -> None:
    app = TranscriptApp()
    app.mainloop()


if __name__ == "__main__":
    main()
