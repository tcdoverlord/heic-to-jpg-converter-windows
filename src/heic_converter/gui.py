from __future__ import annotations

import os
import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .converter import convert_batch
from .logging_setup import application_data_dir
from .models import CollisionPolicy, ConversionOptions, ConversionStatus
from .scanner import discover_files

APP_TITLE = "HEIC to JPG Converter — TCDOVERLORD"

COLLISION_LABELS = {
    "Rename existing (safe)": CollisionPolicy.RENAME,
    "Skip existing": CollisionPolicy.SKIP,
    "Overwrite existing": CollisionPolicy.OVERWRITE,
}


class ConverterWindow(tk.Tk):
    def __init__(self, initial_sources: list[Path] | None = None) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("860x680")
        self.minsize(760, 600)

        self.sources: list[Path] = []
        self.events: queue.Queue[tuple] = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None

        self.output_var = tk.StringVar()
        self.quality_var = tk.IntVar(value=95)
        self.recursive_var = tk.BooleanVar(value=True)
        self.timestamps_var = tk.BooleanVar(value=True)
        self.collision_var = tk.StringVar(value="Rename existing (safe)")
        self.status_var = tk.StringVar(value="Add HEIC files or a folder to begin.")

        self._build_interface()

        if initial_sources:
            self._add_sources(initial_sources)

        self.after(100, self._drain_events)

    def _build_interface(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)
        outer.rowconfigure(7, weight=1)

        title = ttk.Label(
            outer,
            text="HEIC to JPG Converter",
            font=("Segoe UI", 18, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            outer,
            text="Batch-convert iPhone HEIC photos while keeping the originals.",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 12))

        source_frame = ttk.LabelFrame(outer, text="Source files and folders", padding=10)
        source_frame.grid(row=2, column=0, sticky="nsew")
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)

        self.source_list = tk.Listbox(source_frame, selectmode=tk.EXTENDED)
        self.source_list.grid(row=0, column=0, sticky="nsew")
        source_scroll = ttk.Scrollbar(
            source_frame, orient=tk.VERTICAL, command=self.source_list.yview
        )
        source_scroll.grid(row=0, column=1, sticky="ns")
        self.source_list.configure(yscrollcommand=source_scroll.set)

        buttons = ttk.Frame(source_frame)
        buttons.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(buttons, text="Add files", command=self._choose_files).pack(
            side=tk.LEFT
        )
        ttk.Button(buttons, text="Add folder", command=self._choose_folder).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(buttons, text="Remove selected", command=self._remove_selected).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(buttons, text="Clear", command=self._clear_sources).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        output_frame = ttk.Frame(outer)
        output_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        output_frame.columnconfigure(1, weight=1)
        ttk.Label(output_frame, text="Output folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_var).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(output_frame, text="Browse", command=self._choose_output).grid(
            row=0, column=2
        )

        options = ttk.LabelFrame(outer, text="Options", padding=10)
        options.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        ttk.Label(options, text="JPEG quality:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(
            options,
            from_=1,
            to=100,
            textvariable=self.quality_var,
            width=6,
        ).grid(row=0, column=1, sticky="w", padx=(6, 20))

        ttk.Label(options, text="Existing JPG:").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            options,
            state="readonly",
            values=list(COLLISION_LABELS),
            textvariable=self.collision_var,
            width=24,
        ).grid(row=0, column=3, sticky="w", padx=(6, 0))

        ttk.Checkbutton(
            options,
            text="Include subfolders",
            variable=self.recursive_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Checkbutton(
            options,
            text="Preserve file timestamps",
            variable=self.timestamps_var,
        ).grid(row=1, column=2, columnspan=2, sticky="w", pady=(8, 0))

        action_frame = ttk.Frame(outer)
        action_frame.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        self.convert_button = ttk.Button(
            action_frame,
            text="Convert to JPG",
            command=self._start_conversion,
        )
        self.convert_button.pack(side=tk.LEFT)
        self.cancel_button = ttk.Button(
            action_frame,
            text="Cancel",
            command=self._cancel_conversion,
            state=tk.DISABLED,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            action_frame,
            text="Open log folder",
            command=self._open_log_folder,
        ).pack(side=tk.RIGHT)

        self.progress = ttk.Progressbar(outer, mode="determinate")
        self.progress.grid(row=6, column=0, sticky="ew", pady=(12, 0))

        log_frame = ttk.LabelFrame(outer, text="Activity", padding=8)
        log_frame.grid(row=7, column=0, sticky="nsew", pady=(12, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.activity = ScrolledText(log_frame, height=9, state=tk.DISABLED)
        self.activity.grid(row=0, column=0, sticky="nsew")

        ttk.Label(outer, textvariable=self.status_var).grid(
            row=8, column=0, sticky="w", pady=(8, 0)
        )

    def _choose_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Choose HEIC files",
            filetypes=[
                ("HEIC and HEIF images", "*.heic *.heif"),
                ("All files", "*.*"),
            ],
        )
        self._add_sources(Path(item) for item in selected)

    def _choose_folder(self) -> None:
        selected = filedialog.askdirectory(title="Choose a folder containing HEIC files")
        if selected:
            self._add_sources([Path(selected)])

    def _choose_output(self) -> None:
        selected = filedialog.askdirectory(title="Choose output folder")
        if selected:
            self.output_var.set(selected)

    def _add_sources(self, paths) -> None:
        existing = {path.resolve() for path in self.sources if path.exists()}
        for raw_path in paths:
            path = Path(raw_path).expanduser()
            if not path.exists():
                continue
            resolved = path.resolve()
            if resolved in existing:
                continue
            existing.add(resolved)
            self.sources.append(resolved)
            self.source_list.insert(tk.END, str(resolved))

        if self.sources and not self.output_var.get():
            first = self.sources[0]
            base = first if first.is_dir() else first.parent
            self.output_var.set(str(base / "JPG Converted"))

        self.status_var.set(f"{len(self.sources)} source selection(s) ready.")

    def _remove_selected(self) -> None:
        selected = list(self.source_list.curselection())
        for index in reversed(selected):
            self.source_list.delete(index)
            del self.sources[index]
        self.status_var.set(f"{len(self.sources)} source selection(s) ready.")

    def _clear_sources(self) -> None:
        self.sources.clear()
        self.source_list.delete(0, tk.END)
        self.status_var.set("Add HEIC files or a folder to begin.")

    def _set_running(self, running: bool) -> None:
        self.convert_button.configure(state=tk.DISABLED if running else tk.NORMAL)
        self.cancel_button.configure(state=tk.NORMAL if running else tk.DISABLED)

    def _start_conversion(self) -> None:
        if self.worker and self.worker.is_alive():
            return

        if not self.sources:
            messagebox.showwarning(APP_TITLE, "Add at least one HEIC file or folder.")
            return

        output_text = self.output_var.get().strip()
        if not output_text:
            messagebox.showwarning(APP_TITLE, "Choose an output folder.")
            return

        try:
            quality = int(self.quality_var.get())
            if not 1 <= quality <= 100:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning(APP_TITLE, "JPEG quality must be between 1 and 100.")
            return

        output_root = Path(output_text).expanduser().resolve()
        if output_root.exists() and not output_root.is_dir():
            messagebox.showwarning(APP_TITLE, "The output path is not a folder.")
            return

        items = discover_files(
            self.sources,
            recursive=self.recursive_var.get(),
        )

        if not items:
            messagebox.showinfo(APP_TITLE, "No HEIC or HEIF files were found.")
            return

        options = ConversionOptions(
            output_root=output_root,
            quality=quality,
            collision_policy=COLLISION_LABELS[self.collision_var.get()],
            preserve_timestamps=self.timestamps_var.get(),
        )

        self.cancel_event.clear()
        self.progress.configure(maximum=len(items), value=0)
        self._append_activity(f"Starting batch: {len(items)} file(s)")
        self.status_var.set("Converting...")
        self._set_running(True)

        self.worker = threading.Thread(
            target=self._conversion_worker,
            args=(items, options),
            daemon=True,
        )
        self.worker.start()

    def _conversion_worker(self, items, options: ConversionOptions) -> None:
        def progress(index, total, result) -> None:
            self.events.put(("progress", index, total, result))

        results = convert_batch(
            items,
            options,
            cancel_event=self.cancel_event,
            progress_callback=progress,
        )
        self.events.put(("done", results, options.output_root))

    def _cancel_conversion(self) -> None:
        self.cancel_event.set()
        self.status_var.set("Cancellation requested; current file will finish safely.")
        self._append_activity("Cancellation requested.")

    def _drain_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]

                if kind == "progress":
                    _, index, total, result = event
                    self.progress.configure(value=index)
                    destination = f" -> {result.output}" if result.output else ""
                    self._append_activity(
                        f"[{index}/{total}] {result.status.value.upper()}: "
                        f"{result.source.name}{destination}"
                    )
                    if (
                        result.status is ConversionStatus.FAILED
                        and result.message
                    ):
                        self._append_activity(f"    {result.message}")

                elif kind == "done":
                    _, results, output_root = event
                    self._finish_conversion(results, output_root)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._drain_events)

    def _finish_conversion(self, results, output_root: Path) -> None:
        converted = sum(
            result.status is ConversionStatus.CONVERTED for result in results
        )
        skipped = sum(result.status is ConversionStatus.SKIPPED for result in results)
        failed = sum(result.status is ConversionStatus.FAILED for result in results)
        cancelled = any(
            result.status is ConversionStatus.CANCELLED for result in results
        )

        summary = (
            f"Finished: {converted} converted, {skipped} skipped, {failed} failed."
        )
        if cancelled:
            summary += " Batch cancelled."

        self._append_activity(summary)
        self.status_var.set(summary)
        self._set_running(False)

        if failed:
            messagebox.showwarning(
                APP_TITLE,
                summary + "\n\nReview the activity list and log file.",
            )
        else:
            messagebox.showinfo(APP_TITLE, summary + f"\n\nOutput:\n{output_root}")

    def _append_activity(self, text: str) -> None:
        self.activity.configure(state=tk.NORMAL)
        self.activity.insert(tk.END, text + "\n")
        self.activity.see(tk.END)
        self.activity.configure(state=tk.DISABLED)

    def _open_log_folder(self) -> None:
        log_dir = application_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        try:
            if os.name == "nt":
                os.startfile(log_dir)  # type: ignore[attr-defined]
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", str(log_dir)])
            else:
                raise OSError("Opening folders is not supported on this platform.")
        except OSError as exc:
            messagebox.showerror(APP_TITLE, str(exc))


def launch_gui(initial_sources: list[Path] | None = None) -> int:
    window = ConverterWindow(initial_sources=initial_sources)
    window.mainloop()
    return 0
