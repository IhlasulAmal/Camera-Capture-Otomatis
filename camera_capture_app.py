"""Simple webcam capture GUI with timed capture and optional auto-click.

Run with: python scripts/camera_capture_app.py
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk

try:
    import pyautogui
except ImportError:
    pyautogui = None


class CameraCaptureApp:
    """Easy-to-use webcam preview, manual capture, and scheduled capture."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Camera Capture Otomatis")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.minsize(900, 650)

        self.camera: cv2.VideoCapture | None = None
        self.camera_backend = ""
        self.camera_backend_by_choice: dict[str, str] = {}
        self.frame = None
        self.consecutive_read_failures = 0
        self.preview_image: ImageTk.PhotoImage | None = None
        self.last_capture_image: ImageTk.PhotoImage | None = None
        self.last_capture_path: Path | None = None
        self.session_dir: Path | None = None
        self.session_log_path: Path | None = None
        self.session_files: list[str] = []
        self.capture_job: str | None = None
        self.stop_job: str | None = None
        self.capture_count = 0
        self.target_count: int | None = None
        self.session_started_at = 0.0
        self.session_started_datetime: datetime | None = None

        self.output_dir = tk.StringVar(value=str(Path.cwd() / "captures"))
        self.interval_seconds = tk.DoubleVar(value=10.0)
        self.camera_choice = tk.StringVar(value="0")
        self.resolution_choice = tk.StringVar(value="Otomatis (resolusi kamera)")
        self.actual_resolution = tk.StringVar(value="Resolusi aktual: -")
        self.auto_capture = tk.BooleanVar(value=False)
        self.run_mode = tk.StringVar(value="Sampai dihentikan")
        self.limit_value = tk.IntVar(value=5)
        self.auto_click = tk.BooleanVar(value=False)
        self.click_x = tk.IntVar(value=0)
        self.click_y = tk.IntVar(value=0)
        self.status = tk.StringVar(value="Pilih kamera, lalu klik Mulai kamera.")
        self.session_info = tk.StringVar(value="Belum ada sesi capture.")
        self.camera_options: list[str] = []

        self._build_ui()
        self.refresh_cameras()
        self.root.after(30, self._update_preview)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main = ttk.Frame(self.root, padding=10)
        main.grid(sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        preview_frame = ttk.Frame(main)
        preview_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0, 8))
        preview_frame.columnconfigure(0, weight=3)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview = ttk.Label(preview_frame, text="Preview kamera", anchor="center")
        self.preview.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        last_frame = ttk.LabelFrame(preview_frame, text="Last capture", padding=6)
        last_frame.grid(row=0, column=1, sticky="nsew")
        last_frame.columnconfigure(0, weight=1)
        last_frame.rowconfigure(0, weight=1)
        self.last_capture_preview = ttk.Label(last_frame, text="Belum ada capture", anchor="center")
        self.last_capture_preview.grid(row=0, column=0, sticky="nsew")
        self.last_capture_name = ttk.Label(last_frame, text="", anchor="center", wraplength=230)
        self.last_capture_name.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(last_frame, text="Log file berhasil", anchor="w").grid(row=2, column=0, sticky="ew", pady=(10, 3))
        log_frame = ttk.Frame(last_frame)
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.capture_log = tk.Listbox(log_frame, height=7, width=34, activestyle="none")
        self.capture_log.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.capture_log.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.capture_log.configure(yscrollcommand=log_scroll.set)

        controls = ttk.LabelFrame(main, text="Pengaturan capture", padding=8)
        controls.grid(row=1, column=0, columnspan=4, sticky="ew")
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        ttk.Label(controls, text="Kamera:").grid(row=0, column=0, sticky="w")
        self.camera_combo = ttk.Combobox(
            controls, textvariable=self.camera_choice, width=18, state="readonly"
        )
        self.camera_combo.grid(row=0, column=1, sticky="w")
        ttk.Button(controls, text="Cari kamera", command=self.refresh_cameras).grid(row=0, column=2, padx=5, sticky="w")
        ttk.Label(controls, text="Resolusi:").grid(row=0, column=3, sticky="e", padx=(10, 4))
        self.resolution_combo = ttk.Combobox(
            controls, textvariable=self.resolution_choice,
            values=("Otomatis (resolusi kamera)", "640x480", "1280x720", "1920x1080", "3840x2160"),
            state="readonly", width=12,
        )
        self.resolution_combo.grid(row=0, column=4, sticky="w")
        ttk.Label(controls, text="Interval (detik):").grid(row=1, column=3, sticky="e", padx=(10, 4))
        ttk.Spinbox(controls, from_=0.2, to=86400, increment=0.5, textvariable=self.interval_seconds, width=9).grid(row=1, column=4, sticky="w")
        ttk.Label(controls, textvariable=self.actual_resolution).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Label(controls, text="Mode berhenti:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.mode_combo = ttk.Combobox(
            controls, textvariable=self.run_mode,
            values=("Sampai dihentikan", "Durasi (jam)", "Jumlah capture"),
            state="readonly", width=20,
        )
        self.mode_combo.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.mode_combo.bind("<<ComboboxSelected>>", self._update_limit_state)
        ttk.Label(controls, text="Nilai:").grid(row=2, column=2, sticky="e", padx=5, pady=(8, 0))
        self.limit_spin = ttk.Spinbox(controls, from_=1, to=100000, textvariable=self.limit_value, width=9)
        self.limit_spin.grid(row=2, column=3, sticky="w", pady=(8, 0))
        self.limit_hint = ttk.Label(controls, text="tidak digunakan")
        self.limit_hint.grid(row=2, column=4, sticky="w", padx=5, pady=(8, 0))

        ttk.Label(controls, text="Folder penyimpanan:").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.output_dir).grid(row=3, column=1, columnspan=3, sticky="ew", pady=(8, 0))
        ttk.Button(controls, text="Pilih...", command=self.choose_folder).grid(row=3, column=4, pady=(8, 0))

        ttk.Checkbutton(controls, text="Capture otomatis", variable=self.auto_capture, command=self._auto_capture_changed).grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Checkbutton(controls, text="Auto-click setelah capture", variable=self.auto_click).grid(row=4, column=1, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(controls, text="Posisi klik X / Y:").grid(row=4, column=3, sticky="e", pady=(8, 0))
        ttk.Spinbox(controls, from_=0, to=10000, textvariable=self.click_x, width=7).grid(row=4, column=4, sticky="w", pady=(8, 0))
        ttk.Spinbox(controls, from_=0, to=10000, textvariable=self.click_y, width=7).grid(row=5, column=4, sticky="w", pady=(4, 0))
        ttk.Button(controls, text="Ambil posisi kursor", command=self.read_cursor_position).grid(row=5, column=3, sticky="e", pady=(4, 0))

        buttons = ttk.Frame(main)
        buttons.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="Mulai kamera", command=self.start_camera).pack(side="left")
        ttk.Button(buttons, text="Capture sekarang", command=self.capture_now).pack(side="left", padx=5)
        ttk.Button(buttons, text="Mulai auto-capture", command=self.start_auto_capture).pack(side="left")
        ttk.Button(buttons, text="Berhenti", command=self.stop_auto_capture).pack(side="left", padx=5)
        ttk.Button(buttons, text="Stop kamera", command=self.stop_camera).pack(side="left")

        ttk.Label(main, textvariable=self.session_info).grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Label(main, textvariable=self.status).grid(row=4, column=0, columnspan=4, sticky="w", pady=(4, 0))
        self._update_limit_state()

    def _backend_candidates(self) -> list[tuple[str, int]]:
        candidates = [("DirectShow", cv2.CAP_DSHOW), ("Media Foundation", cv2.CAP_MSMF), ("Default", cv2.CAP_ANY)]
        available: list[tuple[str, int]] = []
        seen: set[int] = set()
        for name, backend in candidates:
            if backend not in seen:
                available.append((name, backend))
                seen.add(backend)
        return available

    def _open_camera(self, index: int, preferred_backend: str | None = None) -> tuple[cv2.VideoCapture | None, str, object | None]:
        candidates = self._backend_candidates()
        if preferred_backend:
            candidates.sort(key=lambda item: 0 if item[0] == preferred_backend else 1)
        for backend_name, backend in candidates:
            camera = cv2.VideoCapture(index, backend)
            if not camera.isOpened():
                camera.release()
                continue
            if self.resolution_choice.get() != "Otomatis (resolusi kamera)":
                width, height = (int(value) for value in self.resolution_choice.get().split("x"))
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            ok, frame = camera.read()
            if ok and frame is not None and getattr(frame, "size", 0) > 0:
                return camera, backend_name, frame
            camera.release()
        return None, "", None

    def refresh_cameras(self) -> None:
        found: list[str] = []
        self.camera_backend_by_choice.clear()
        for index in range(10):
            camera, backend_name, frame = self._open_camera(index)
            if camera is not None:
                label = f"{index} - Kamera {index} ({backend_name})"
                found.append(label)
                self.camera_backend_by_choice[label] = backend_name
                camera.release()
        self.camera_options = found
        self.camera_combo["values"] = found
        if found:
            if self.camera_choice.get() not in found:
                self.camera_choice.set(found[0])
            self.status.set(f"Ditemukan {len(found)} kamera dengan frame valid.")
        else:
            self.camera_choice.set("")
            self.status.set("Tidak ada kamera dengan frame valid. Periksa izin, driver, dan aplikasi lain.")

    def _camera_index(self) -> int:
        return int(self.camera_choice.get().split(" ", 1)[0])

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)

    def start_camera(self) -> None:
        if self.camera is not None and self.camera.isOpened():
            return
        try:
            index = self._camera_index()
        except (ValueError, IndexError):
            messagebox.showwarning("Kamera", "Pilih kamera terlebih dahulu.")
            return
        preferred_backend = self.camera_backend_by_choice.get(self.camera_choice.get())
        camera, backend_name, frame = self._open_camera(index, preferred_backend)
        if camera is None or frame is None:
            messagebox.showerror(
                "Kamera",
                "Kamera terdeteksi tetapi tidak mengirim frame valid. "
                "Tutup aplikasi lain yang memakai kamera lalu klik Cari kamera.",
            )
            return

        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_resolution.set(f"Resolusi aktual: {actual_width}x{actual_height}")
        self.camera = camera
        self.camera_backend = backend_name
        self.frame = frame
        self.consecutive_read_failures = 0
        self.status.set(f"Kamera aktif ({backend_name}). Preview siap.")

    def stop_camera(self) -> None:
        self.stop_auto_capture()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.camera_backend = ""
        self.consecutive_read_failures = 0
        self.frame = None
        self.preview.configure(image="", text="Preview kamera")
        self.preview_image = None
        self.status.set("Kamera dihentikan.")

    def _update_preview(self) -> None:
        if self.camera is not None:
            ok, frame = self.camera.read()
            if ok and frame is not None and frame.size > 0:
                self.frame = frame
                self.consecutive_read_failures = 0
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb)
                image.thumbnail((1000, 620))
                self.preview_image = ImageTk.PhotoImage(image)
                self.preview.configure(image=self.preview_image, text="")
            else:
                self.consecutive_read_failures += 1
                if self.consecutive_read_failures >= 30:
                    self.status.set(f"Frame kamera gagal dibaca ({self.camera_backend}).")
        self.root.after(30, self._update_preview)

    def capture_now(self) -> bool:
        if self.frame is None:
            self.status.set("Belum ada frame kamera untuk disimpan.")
            return False
        output = self.session_dir or self._create_session_dir()
        now = datetime.now()
        filename = output / f"cap{self.capture_count + 1:04d}-{now:%H%M%S}-{now:%Y-%m-%d}.jpg"
        if not cv2.imwrite(str(filename), self.frame):
            self.status.set("Gagal menyimpan gambar.")
            return False
        self._show_last_capture(filename)
        self.capture_log.insert(tk.END, f"{self.capture_count + 1:04d}  {filename.name}")
        self.capture_log.see(tk.END)
        self.session_files.append(filename.name)
        self.capture_count += 1
        self._write_session_log()
        self.session_info.set(f"Capture sesi ini: {self.capture_count} | Folder: {output.name}")
        self.status.set(f"Tersimpan: {filename}")
        if self.auto_click.get():
            self._click_position()
        return True

    def _create_session_dir(self) -> Path:
        timestamp = datetime.now().strftime("Cap-Session_%Y-%m-%d-%H")
        session_dir = Path(self.output_dir.get()).expanduser() / timestamp
        session_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir = session_dir
        return session_dir

    def _start_new_session(self) -> None:
        self.session_dir = self._create_session_dir()
        self.session_log_path = self.session_dir / "session_log.json"
        self.session_files = []
        self.capture_count = 0
        self._write_session_log(status="initialized")
        self.capture_log.delete(0, tk.END)
        self.last_capture_preview.configure(image="", text="Belum ada capture")
        self.last_capture_name.configure(text="")
        self.last_capture_image = None
        self.session_info.set(f"Sesi baru: {self.session_dir.name}")

    def _show_last_capture(self, filename: Path) -> None:
        image = Image.open(filename)
        image.thumbnail((300, 260))
        self.last_capture_image = ImageTk.PhotoImage(image)
        self.last_capture_preview.configure(image=self.last_capture_image, text="")
        self.last_capture_name.configure(text=filename.name)
        self.last_capture_path = filename

    def _click_position(self) -> None:
        if pyautogui is None:
            self.status.set("Capture tersimpan, tetapi pyautogui belum terpasang.")
            return
        try:
            pyautogui.click(self.click_x.get(), self.click_y.get())
        except (OSError, ValueError) as exc:
            self.status.set(f"Auto-click gagal: {exc}")

    def read_cursor_position(self) -> None:
        if pyautogui is None:
            messagebox.showwarning("Auto-click", "Install pyautogui terlebih dahulu.")
            return
        position = pyautogui.position()
        self.click_x.set(position.x)
        self.click_y.set(position.y)
        self.status.set(f"Posisi kursor: ({position.x}, {position.y})")

    def _update_limit_state(self, _event: object = None) -> None:
        mode = self.run_mode.get()
        enabled = mode != "Sampai dihentikan"
        self.limit_spin.configure(state="normal" if enabled else "disabled")
        self.limit_hint.configure(text="jam" if mode == "Durasi (jam)" else "gambar" if enabled else "tidak digunakan")

    def _auto_capture_changed(self) -> None:
        if self.auto_capture.get():
            self.start_auto_capture()
        else:
            self.stop_auto_capture()

    def start_auto_capture(self) -> None:
        if self.camera is None:
            self.status.set("Mulai kamera terlebih dahulu.")
            self.auto_capture.set(False)
            return
        self._cancel_jobs()
        self._start_new_session()
        self.target_count = None
        self.session_started_at = time.monotonic()
        self.session_started_datetime = datetime.now()
        self._write_session_log(status="running")
        mode = self.run_mode.get()
        if mode == "Jumlah capture":
            self.target_count = max(1, int(self.limit_value.get()))
        elif mode == "Durasi (jam)":
            hours = max(0.01, float(self.limit_value.get()))
            self.stop_job = self.root.after(int(hours * 3600 * 1000), self.stop_auto_capture)
        self.auto_capture.set(True)
        self.status.set("Auto-capture aktif.")
        self._schedule_capture(first_capture=True)

    def stop_auto_capture(self) -> None:
        self._cancel_jobs()
        was_running = self.auto_capture.get()
        self.auto_capture.set(False)
        if self.session_started_at and was_running:
            elapsed = time.monotonic() - self.session_started_at
            self._write_session_log(status="completed", finished_at=datetime.now(), elapsed_seconds=elapsed)
            self.status.set(f"Auto-capture berhenti. {self.capture_count} gambar, durasi {elapsed / 60:.1f} menit.")

    def _write_session_log(
        self,
        status: str = "running",
        finished_at: datetime | None = None,
        elapsed_seconds: float | None = None,
    ) -> None:
        if self.session_log_path is None:
            return
        started = self.session_started_datetime
        if elapsed_seconds is None and self.session_started_at:
            elapsed_seconds = time.monotonic() - self.session_started_at
        log = {
            "application": "Camera Capture Otomatis",
            "status": status,
            "session": {
                "folder": str(self.session_dir),
                "started_at": started.isoformat(timespec="seconds") if started else None,
                "finished_at": finished_at.isoformat(timespec="seconds") if finished_at else None,
                "duration_seconds": round(elapsed_seconds, 2) if elapsed_seconds is not None else None,
            },
            "settings": {
                "camera": self.camera_choice.get(),
                "camera_index": self._camera_index() if self.camera_choice.get() else None,
                "requested_resolution": self.resolution_choice.get(),
                "actual_resolution": self.actual_resolution.get().replace("Resolusi aktual: ", ""),
                "interval_seconds": float(self.interval_seconds.get()),
                "stop_mode": self.run_mode.get(),
                "stop_value": int(self.limit_value.get()),
                "output_root": str(Path(self.output_dir.get()).expanduser()),
            },
            "result": {
                "capture_count": self.capture_count,
                "files": self.session_files,
            },
        }
        self.session_log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _schedule_capture(self, first_capture: bool = False) -> None:
        delay = 0 if first_capture else max(0.2, float(self.interval_seconds.get())) * 1000
        self.capture_job = self.root.after(int(delay), self._timed_capture)

    def _timed_capture(self) -> None:
        self.capture_job = None
        if not self.auto_capture.get() or self.camera is None:
            return
        self.capture_now()
        if self.target_count is not None and self.capture_count >= self.target_count:
            self.stop_auto_capture()
        else:
            self._schedule_capture()

    def _cancel_jobs(self) -> None:
        for job_name in ("capture_job", "stop_job"):
            job = getattr(self, job_name)
            if job is not None:
                self.root.after_cancel(job)
                setattr(self, job_name, None)

    def close(self) -> None:
        self.stop_camera()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    root.geometry("1050x800")
    CameraCaptureApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
