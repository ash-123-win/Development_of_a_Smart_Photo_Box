import tkinter as tk
from PIL import Image, ImageTk


class PhotoBoothUI:
    def __init__(
        self,
        root: tk.Tk,
        on_start_session,
        on_capture_requested,
        on_delete_requested,
        on_print_requested,
    ):
        self.root = root
        self.on_start_session = on_start_session
        self.on_capture_requested = on_capture_requested
        self.on_delete_requested = on_delete_requested
        self.on_print_requested = on_print_requested

        self.camera = None
        self._tk_img = None
        self._preview_running = False

        self._build_base()
        self.show_welcome()

    def _build_base(self):
        self.root.title("Photo Automate")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bottom = tk.Frame(self.root, bg="black")
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self._btn_opts = dict(
            bg="black",
            fg="white",
            activebackground="black",
            activeforeground="white",
            bd=0,
            highlightthickness=0,
        )

    # ---------- Screens ----------

    def show_welcome(self):
        self._stop_preview()
        self._clear()

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        self.canvas.create_text(
            w // 2,
            h // 2 - 90,
            text="Photo Automate",
            fill="white",
            font=("DejaVu Sans", 54, "bold"),
        )
        self.canvas.create_text(
            w // 2,
            h // 2 - 25,
            text="Tap to start your session",
            fill="white",
            font=("DejaVu Sans", 22),
        )

        start_btn = tk.Button(
            self.bottom,
            text="START SESSION",
            command=self.on_start_session,
            **self._btn_opts,
            font=("DejaVu Sans", 26, "bold"),
        )
        start_btn.pack(pady=26)

    def show_live_preview(self, camera):
        self._clear()
        self.camera = camera
        self._preview_running = True

        capture_btn = tk.Button(
            self.bottom,
            text="📷",
            command=self.on_capture_requested,
            **self._btn_opts,
            font=("Noto Color Emoji", 40),
        )
        capture_btn.pack(pady=16)

        self._update_preview()

    def show_captured_image(self, image_path):
        self._stop_preview()
        self._clear()

        img = Image.open(image_path)

        cw = self.canvas.winfo_width() or self.root.winfo_screenwidth()
        ch = self.canvas.winfo_height() or (self.root.winfo_screenheight() - 120)

        img = self._fit(img, cw, ch)
        self._tk_img = ImageTk.PhotoImage(img)

        self.canvas.create_image(
            cw // 2, ch // 2,
            image=self._tk_img,
            anchor=tk.CENTER,
        )

        row = tk.Frame(self.bottom, bg="black")
        row.pack(pady=18)

        print_btn = tk.Button(
    row,
    text="🖨 Print",
    command=self.on_print_requested,
    **self._btn_opts,
    font=("DejaVu Sans", 26, "bold"),
)
        print_btn.pack(side=tk.LEFT, padx=30)

        delete_btn = tk.Button(
    row,
    text="🗑 Delete",
    command=self.on_delete_requested,
    **self._btn_opts,
    font=("DejaVu Sans", 26, "bold"),
)
        delete_btn.pack(side=tk.LEFT, padx=30)

    # ---------- Preview loop ----------

    def _update_preview(self):
        if not self._preview_running or self.camera is None:
            return

        try:
            frame = self.camera.get_preview_frame_rgb()
            img = Image.fromarray(frame)

            w = self.canvas.winfo_width() or self.root.winfo_screenwidth()
            h = self.canvas.winfo_height() or (self.root.winfo_screenheight() - 120)

            img = self._fit(img, w, h)
            self._tk_img = ImageTk.PhotoImage(img)

            self.canvas.delete("preview")
            self.canvas.create_image(
                w // 2, h // 2,
                image=self._tk_img,
                anchor=tk.CENTER,
                tags="preview",
            )
        except Exception:
            pass

        self.root.after(33, self._update_preview)

    def _stop_preview(self):
        self._preview_running = False

    def _clear(self):
        self.canvas.delete("all")
        for w in self.bottom.winfo_children():
            w.destroy()

    @staticmethod
    def _fit(img, w, h):
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        return img.resize((int(iw * scale), int(ih * scale)))
