import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTabWidget, QScrollArea,
    QGroupBox, QGridLayout, QComboBox, QSlider, QSpinBox,
    QStatusBar, QSplitter, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ─────────────────────────────────────────────
#  Helper: numpy array → QPixmap
# ─────────────────────────────────────────────
def ndarray_to_pixmap(img: np.ndarray) -> QPixmap:
    if img is None:
        return QPixmap()
    if len(img.shape) == 2:
        h, w = img.shape
        qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
    else:
        h, w, c = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, w, h, w * c, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


def scale_pixmap(pixmap: QPixmap, max_w=480, max_h=380) -> QPixmap:
    if pixmap.isNull():
        return pixmap
    return pixmap.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)


# ─────────────────────────────────────────────
#  Image label with placeholder
# ─────────────────────────────────────────────
class ImageLabel(QLabel):
    def __init__(self, placeholder="Belum ada gambar"):
        super().__init__(placeholder)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(360, 280)
        self.setStyleSheet("""
            QLabel {
                background: #1a1f2e;
                border: 2px dashed #3a4060;
                border-radius: 10px;
                color: #555e7a;
                font-size: 13px;
            }
        """)
        self._placeholder = placeholder

    def set_image(self, img: np.ndarray):
        if img is None:
            self.setText(self._placeholder)
            return
        px = scale_pixmap(ndarray_to_pixmap(img))
        self.setPixmap(px)
        self.setStyleSheet("""
            QLabel {
                background: #1a1f2e;
                border: 2px solid #3a6fd8;
                border-radius: 10px;
            }
        """)


# ─────────────────────────────────────────────
#  Matplotlib canvas for histogram
# ─────────────────────────────────────────────
class HistogramCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 3), facecolor='#1a1f2e')
        super().__init__(self.fig)
        self.setParent(parent)

    def plot(self, img: np.ndarray):
        self.fig.clear()
        channels_info = [
            (0, '#5b9ef5', 'Blue'),
            (1, '#5be87a', 'Green'),
            (2, '#f55b5b', 'Red'),
        ]

        ax = self.fig.add_subplot(111, facecolor='#131827')
        ax.tick_params(colors='#8892b0')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2a3050')

        if len(img.shape) == 2:
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            ax.plot(hist, color='#5b9ef5', linewidth=1.2)
            ax.fill_between(range(256), hist.flatten(), alpha=0.3, color='#5b9ef5')
            ax.set_title('Histogram Grayscale', color='#c8d0e7', fontsize=11)
        else:
            for ch, col, lbl in channels_info:
                hist = cv2.calcHist([img], [ch], None, [256], [0, 256])
                ax.plot(hist, color=col, linewidth=1.2, label=lbl)
                ax.fill_between(range(256), hist.flatten(), alpha=0.15, color=col)
            ax.set_title('Histogram RGB', color='#c8d0e7', fontsize=11)
            ax.legend(facecolor='#1a1f2e', edgecolor='#3a4060',
                      labelcolor='#c8d0e7', fontsize=9)

        ax.set_xlim([0, 256])
        ax.set_xlabel('Intensitas Piksel', color='#8892b0', fontsize=9)
        ax.set_ylabel('Frekuensi', color='#8892b0', fontsize=9)
        self.fig.tight_layout()
        self.draw()


# ─────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.current_image = None
        self._setup_ui()

    # ── UI setup ──────────────────────────────
    def _setup_ui(self):
        self.setWindowTitle("🖼  CitraLab — Aplikasi Pengolahan Citra Digital")
        self.setMinimumSize(1100, 720)
        self._apply_dark_theme()

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("color: #8892b0; background: #0d1117; border-top: 1px solid #1e2433;")
        self.status.showMessage("Selamat datang di CitraLab! Mulai dengan memuat gambar.")

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        main_layout.addWidget(self._build_header())

        # Body
        body = QSplitter(Qt.Horizontal)
        body.setStyleSheet("QSplitter::handle { background: #1e2433; width: 3px; }")
        body.addWidget(self._build_left_panel())
        body.addWidget(self._build_tabs())
        body.setSizes([260, 840])
        main_layout.addWidget(body, 1)

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #0d1117; }
            QWidget { background: #0d1117; color: #c8d0e7; font-family: 'Segoe UI', sans-serif; }
            QTabWidget::pane { border: 1px solid #1e2433; background: #111827; }
            QTabBar::tab {
                background: #131827; color: #8892b0;
                padding: 9px 20px; border: none;
                border-top: 3px solid transparent;
                font-size: 12px;
            }
            QTabBar::tab:selected { color: #5b9ef5; border-top: 3px solid #5b9ef5; background: #111827; }
            QGroupBox {
                border: 1px solid #1e2433; border-radius: 8px;
                margin-top: 14px; padding: 10px;
                font-size: 12px; color: #8892b0;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #5b9ef5; }
            QPushButton {
                background: #1e2d4f; color: #5b9ef5;
                border: 1px solid #2a4070; border-radius: 7px;
                padding: 8px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #254070; border-color: #5b9ef5; }
            QPushButton:pressed { background: #1a3060; }
            QPushButton#primary {
                background: #1a4fd6; color: white;
                border: none; font-weight: bold;
            }
            QPushButton#primary:hover { background: #2060f0; }
            QPushButton#danger { background: #4a1a1a; color: #f55b5b; border-color: #703030; }
            QPushButton#danger:hover { background: #602020; }
            QComboBox {
                background: #1a1f2e; color: #c8d0e7;
                border: 1px solid #2a3050; border-radius: 6px;
                padding: 5px 10px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #1a1f2e; color: #c8d0e7; selection-background-color: #2a4070; }
            QSlider::groove:horizontal { background: #1e2433; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #5b9ef5; width: 14px; height: 14px; border-radius: 7px; margin: -4px 0; }
            QSlider::sub-page:horizontal { background: #3a6fd8; border-radius: 3px; }
            QSpinBox {
                background: #1a1f2e; color: #c8d0e7;
                border: 1px solid #2a3050; border-radius: 6px; padding: 4px 8px;
            }
            QScrollArea { border: none; }
            QLabel { color: #c8d0e7; }
        """)

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #111827; border-bottom: 1px solid #1e2433;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)

        title = QLabel("🖼  CitraLab")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #5b9ef5; letter-spacing: 1px;")

        subtitle = QLabel("Aplikasi Pengolahan Citra Digital — IK23")
        subtitle.setStyleSheet("font-size: 11px; color: #555e7a;")

        hl.addWidget(title)
        hl.addWidget(subtitle)
        hl.addStretch()

        btn_open = QPushButton("📂  Buka Gambar")
        btn_open.setObjectName("primary")
        btn_open.setFixedHeight(36)
        btn_open.clicked.connect(self.open_image)

        btn_save = QPushButton("💾  Simpan Hasil")
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self.save_image)

        btn_reset = QPushButton("🔄  Reset")
        btn_reset.setObjectName("danger")
        btn_reset.setFixedHeight(36)
        btn_reset.clicked.connect(self.reset_image)

        hl.addWidget(btn_open)
        hl.addWidget(btn_save)
        hl.addWidget(btn_reset)
        return header

    def _build_left_panel(self):
        panel = QWidget()
        panel.setFixedWidth(255)
        panel.setStyleSheet("background: #0d1117; border-right: 1px solid #1e2433;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)

        # Image preview
        grp = QGroupBox("Preview Asli")
        g_layout = QVBoxLayout(grp)
        self.preview_label = QLabel("Belum ada gambar")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(180)
        self.preview_label.setStyleSheet("""
            background: #1a1f2e; border: 2px dashed #2a3050;
            border-radius: 8px; color: #555e7a; font-size: 11px;
        """)
        g_layout.addWidget(self.preview_label)
        layout.addWidget(grp)

        # Image info
        grp2 = QGroupBox("Info Gambar")
        g2_layout = QVBoxLayout(grp2)
        self.info_label = QLabel("—")
        self.info_label.setStyleSheet("font-size: 11px; color: #8892b0; line-height: 1.6;")
        self.info_label.setWordWrap(True)
        g2_layout.addWidget(self.info_label)
        layout.addWidget(grp2)

        layout.addStretch()

        tip = QLabel("💡 Tip: Buka gambar dulu sebelum\nmelakukan proses pengolahan.")
        tip.setStyleSheet("font-size: 10px; color: #404860; padding: 6px;")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        return panel

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_display(), "🖼  Tampilkan")
        self.tabs.addTab(self._tab_basic_process(), "⚙  Proses Dasar")
        self.tabs.addTab(self._tab_arithmetic(), "➕  Aritmatika & Logika")
        self.tabs.addTab(self._tab_histogram(), "📊  Histogram")
        self.tabs.addTab(self._tab_convolution(), "🔍  Konvolusi / Filter")
        self.tabs.addTab(self._tab_morphology(), "🔬  Morfologi")
        return self.tabs

    # ── Tab 1: Display ─────────────────────────
    def _tab_display(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("Gambar Asli (Original)")
        lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #5b9ef5;")
        layout.addWidget(lbl)

        self.display_img = ImageLabel("Buka gambar terlebih dahulu")
        layout.addWidget(self.display_img, 1)
        return w

    # ── Tab 2: Basic Process ───────────────────
    def _tab_basic_process(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Buttons
        btn_row = QHBoxLayout()
        btn_gray = QPushButton("🌑  Grayscale")
        btn_gray.clicked.connect(self.to_grayscale)
        btn_bin = QPushButton("⬛  Biner (Threshold)")
        btn_bin.clicked.connect(self.to_binary)
        btn_row.addWidget(btn_gray)
        btn_row.addWidget(btn_bin)

        # Threshold slider
        thresh_row = QHBoxLayout()
        thresh_lbl = QLabel("Threshold:")
        thresh_lbl.setStyleSheet("font-size: 11px; color: #8892b0; min-width: 70px;")
        self.thresh_slider = QSlider(Qt.Horizontal)
        self.thresh_slider.setRange(0, 255)
        self.thresh_slider.setValue(127)
        self.thresh_val_lbl = QLabel("127")
        self.thresh_val_lbl.setStyleSheet("min-width: 28px; color: #5b9ef5;")
        self.thresh_slider.valueChanged.connect(lambda v: self.thresh_val_lbl.setText(str(v)))
        thresh_row.addWidget(thresh_lbl)
        thresh_row.addWidget(self.thresh_slider)
        thresh_row.addWidget(self.thresh_val_lbl)

        layout.addLayout(btn_row)
        layout.addLayout(thresh_row)

        # Image panels
        img_row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Input"))
        self.basic_in = ImageLabel()
        left.addWidget(self.basic_in)

        right = QVBoxLayout()
        right.addWidget(QLabel("Output"))
        self.basic_out = ImageLabel()
        right.addWidget(self.basic_out)

        img_row.addLayout(left)
        img_row.addLayout(right)
        layout.addLayout(img_row, 1)
        return w

    # ── Tab 3: Arithmetic & Logic ──────────────
    def _tab_arithmetic(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Arithmetic
        grp_arith = QGroupBox("Operasi Aritmatika")
        a_layout = QVBoxLayout(grp_arith)
        row1 = QHBoxLayout()

        self.arith_combo = QComboBox()
        self.arith_combo.addItems(["Penjumlahan (Add)", "Pengurangan (Subtract)",
                                   "Perkalian (Multiply)", "Pembagian (Divide)"])
        self.arith_scalar = QSpinBox()
        self.arith_scalar.setRange(0, 255)
        self.arith_scalar.setValue(50)
        self.arith_scalar.setPrefix("Nilai: ")
        btn_arith = QPushButton("▶  Jalankan")
        btn_arith.clicked.connect(self.apply_arithmetic)
        row1.addWidget(self.arith_combo, 2)
        row1.addWidget(self.arith_scalar, 1)
        row1.addWidget(btn_arith)
        a_layout.addLayout(row1)
        layout.addWidget(grp_arith)

        # Logic
        grp_logic = QGroupBox("Operasi Logika")
        l_layout = QVBoxLayout(grp_logic)
        row2 = QHBoxLayout()
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["AND", "OR", "NOT", "XOR"])
        btn_logic = QPushButton("▶  Jalankan")
        btn_logic.clicked.connect(self.apply_logic)
        row2.addWidget(self.logic_combo)
        row2.addWidget(btn_logic)
        l_layout.addLayout(row2)
        layout.addWidget(grp_logic)

        # Image display
        img_row = QHBoxLayout()
        lv = QVBoxLayout(); lv.addWidget(QLabel("Input"))
        self.arith_in = ImageLabel()
        lv.addWidget(self.arith_in)
        rv = QVBoxLayout(); rv.addWidget(QLabel("Output"))
        self.arith_out = ImageLabel()
        rv.addWidget(self.arith_out)
        img_row.addLayout(lv); img_row.addLayout(rv)
        layout.addLayout(img_row, 1)
        return w

    # ── Tab 4: Histogram ───────────────────────
    def _tab_histogram(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_hist = QPushButton("📊  Tampilkan Histogram")
        btn_hist.setObjectName("primary")
        btn_hist.clicked.connect(self.show_histogram)
        btn_row.addWidget(btn_hist)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.hist_canvas = HistogramCanvas()
        layout.addWidget(self.hist_canvas, 1)

        self.hist_img_lbl = ImageLabel("Gambar yang dianalisis akan tampil di sini")
        self.hist_img_lbl.setMaximumHeight(200)
        layout.addWidget(self.hist_img_lbl)
        return w

    # ── Tab 5: Convolution ─────────────────────
    def _tab_convolution(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        grp = QGroupBox("Pilih Filter Konvolusi")
        g = QVBoxLayout(grp)
        row = QHBoxLayout()
        self.conv_combo = QComboBox()
        self.conv_combo.addItems([
            "Blurring (Gaussian Blur)",
            "Sharpening",
            "Edge Detection (Sobel)",
            "Edge Detection (Laplacian)",
            "Emboss",
        ])
        self.conv_ksize = QSpinBox()
        self.conv_ksize.setRange(3, 21)
        self.conv_ksize.setSingleStep(2)
        self.conv_ksize.setValue(5)
        self.conv_ksize.setPrefix("Kernel: ")
        btn_conv = QPushButton("▶  Terapkan Filter")
        btn_conv.setObjectName("primary")
        btn_conv.clicked.connect(self.apply_convolution)
        row.addWidget(self.conv_combo, 2)
        row.addWidget(self.conv_ksize)
        row.addWidget(btn_conv)
        g.addLayout(row)
        layout.addWidget(grp)

        img_row = QHBoxLayout()
        lv = QVBoxLayout(); lv.addWidget(QLabel("Input"))
        self.conv_in = ImageLabel()
        lv.addWidget(self.conv_in)
        rv = QVBoxLayout(); rv.addWidget(QLabel("Output"))
        self.conv_out = ImageLabel()
        rv.addWidget(self.conv_out)
        img_row.addLayout(lv); img_row.addLayout(rv)
        layout.addLayout(img_row, 1)
        return w

    # ── Tab 6: Morphology ─────────────────────
    def _tab_morphology(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        grp = QGroupBox("Parameter Morfologi")
        g = QGridLayout(grp)

        g.addWidget(QLabel("Operasi:"), 0, 0)
        self.morph_op = QComboBox()
        self.morph_op.addItems(["Dilasi", "Erosi", "Opening (Erosi→Dilasi)", "Closing (Dilasi→Erosi)"])
        g.addWidget(self.morph_op, 0, 1)

        g.addWidget(QLabel("Elemen Penstruktur (SE):"), 1, 0)
        self.morph_se = QComboBox()
        self.morph_se.addItems([
            "Persegi (Rectangle)",
            "Ellipse",
            "Cross (Plus)",
            "Diamond",
        ])
        g.addWidget(self.morph_se, 1, 1)

        g.addWidget(QLabel("Ukuran SE:"), 2, 0)
        self.morph_size = QSpinBox()
        self.morph_size.setRange(3, 21)
        self.morph_size.setSingleStep(2)
        self.morph_size.setValue(5)
        g.addWidget(self.morph_size, 2, 1)

        btn_morph = QPushButton("▶  Terapkan Morfologi")
        btn_morph.setObjectName("primary")
        btn_morph.clicked.connect(self.apply_morphology)
        g.addWidget(btn_morph, 3, 0, 1, 2)

        layout.addWidget(grp)

        img_row = QHBoxLayout()
        lv = QVBoxLayout(); lv.addWidget(QLabel("Input (Binary)"))
        self.morph_in = ImageLabel()
        lv.addWidget(self.morph_in)
        rv = QVBoxLayout(); rv.addWidget(QLabel("Output"))
        self.morph_out = ImageLabel()
        rv.addWidget(self.morph_out)
        img_row.addLayout(lv); img_row.addLayout(rv)
        layout.addLayout(img_row, 1)
        return w

    # ─────────────────────────────────────────────
    #  Actions
    # ─────────────────────────────────────────────
    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Buka Gambar", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            QMessageBox.critical(self, "Error", "Gagal membuka gambar!")
            return
        self.original_image = img
        self.current_image = img.copy()
        self._refresh_all_inputs()
        h, w = img.shape[:2]
        ch = img.shape[2] if len(img.shape) == 3 else 1
        self.info_label.setText(
            f"<b>Ukuran:</b> {w} × {h} px<br>"
            f"<b>Channel:</b> {ch}<br>"
            f"<b>Tipe:</b> {img.dtype}<br>"
            f"<b>File:</b> {path.split('/')[-1]}"
        )
        # Preview
        px = scale_pixmap(ndarray_to_pixmap(img), 220, 170)
        self.preview_label.setPixmap(px)
        self.preview_label.setStyleSheet("background: #1a1f2e; border-radius: 8px;")
        self.status.showMessage(f"✅  Gambar dimuat: {path}")

    def _refresh_all_inputs(self):
        img = self.original_image
        self.display_img.set_image(img)
        self.basic_in.set_image(img)
        self.arith_in.set_image(img)
        self.conv_in.set_image(img)

    def save_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar untuk disimpan!")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Gambar", "hasil_proses.png",
            "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        if path:
            cv2.imwrite(path, self.current_image)
            self.status.showMessage(f"✅  Gambar disimpan ke: {path}")

    def reset_image(self):
        if self.original_image is None:
            return
        self.current_image = self.original_image.copy()
        self._refresh_all_inputs()
        self.basic_out.set_image(None)
        self.arith_out.set_image(None)
        self.conv_out.set_image(None)
        self.morph_in.set_image(None)
        self.morph_out.set_image(None)
        self.status.showMessage("🔄  Gambar direset ke aslinya.")

    def _check_image(self) -> bool:
        if self.original_image is None:
            QMessageBox.warning(self, "Peringatan", "Buka gambar terlebih dahulu!")
            return False
        return True

    # ── Basic ──────────────────────────────────
    def to_grayscale(self):
        if not self._check_image(): return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        self.current_image = gray
        self.basic_out.set_image(gray)
        self.status.showMessage("⚙  Konversi ke Grayscale selesai.")

    def to_binary(self):
        if not self._check_image(): return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        t = self.thresh_slider.value()
        _, binary = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
        self.current_image = binary
        self.basic_out.set_image(binary)
        self.status.showMessage(f"⚙  Konversi ke Biner (threshold={t}) selesai.")

    # ── Arithmetic & Logic ─────────────────────
    def apply_arithmetic(self):
        if not self._check_image(): return
        img = self.original_image.astype(np.float32)
        v = self.arith_scalar.value()
        op = self.arith_combo.currentIndex()
        scalar = np.full_like(img, v, dtype=np.float32)

        if op == 0:
            result = cv2.add(img, scalar)
        elif op == 1:
            result = cv2.subtract(img, scalar)
        elif op == 2:
            result = img * (v / 50.0)
        else:
            result = img / max(v, 1)

        result = np.clip(result, 0, 255).astype(np.uint8)
        self.current_image = result
        self.arith_in.set_image(self.original_image)
        self.arith_out.set_image(result)
        self.status.showMessage(f"➕  Operasi aritmatika '{self.arith_combo.currentText()}' selesai.")

    def apply_logic(self):
        if not self._check_image(): return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        mask = np.full_like(bw, 128)
        op = self.logic_combo.currentText()

        if op == "AND":
            result = cv2.bitwise_and(bw, mask)
        elif op == "OR":
            result = cv2.bitwise_or(bw, mask)
        elif op == "NOT":
            result = cv2.bitwise_not(bw)
        else:
            result = cv2.bitwise_xor(bw, mask)

        self.current_image = result
        self.arith_in.set_image(self.original_image)
        self.arith_out.set_image(result)
        self.status.showMessage(f"🔣  Operasi logika '{op}' selesai.")

    # ── Histogram ─────────────────────────────
    def show_histogram(self):
        if not self._check_image(): return
        self.hist_canvas.plot(self.original_image)
        self.hist_img_lbl.set_image(self.original_image)
        self.status.showMessage("📊  Histogram ditampilkan.")

    # ── Convolution ────────────────────────────
    def apply_convolution(self):
        if not self._check_image(): return
        img = self.original_image
        k = self.conv_ksize.value()
        if k % 2 == 0:
            k += 1
        op = self.conv_combo.currentIndex()

        if op == 0:  # Gaussian Blur
            result = cv2.GaussianBlur(img, (k, k), 0)
        elif op == 1:  # Sharpening
            kernel = np.array([[-1, -1, -1],
                                [-1,  9, -1],
                                [-1, -1, -1]])
            result = cv2.filter2D(img, -1, kernel)
        elif op == 2:  # Sobel
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
            sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
            result = cv2.convertScaleAbs(cv2.magnitude(sx, sy))
        elif op == 3:  # Laplacian
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            result = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F, ksize=k))
        else:  # Emboss
            kernel = np.array([[-2, -1, 0],
                                [-1,  1, 1],
                                [ 0,  1, 2]])
            result = cv2.filter2D(img, -1, kernel)

        self.current_image = result
        self.conv_in.set_image(img)
        self.conv_out.set_image(result)
        self.status.showMessage(f"🔍  Filter '{self.conv_combo.currentText()}' diterapkan.")

    # ── Morphology ─────────────────────────────
    def apply_morphology(self):
        if not self._check_image(): return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        size = self.morph_size.value()
        se_idx = self.morph_se.currentIndex()
        op_idx = self.morph_op.currentIndex()

        # Build SE
        if se_idx == 0:
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
        elif se_idx == 1:
            se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        elif se_idx == 2:
            se = cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))
        else:  # Diamond – approximate with cross + dilation
            base = cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))
            se = cv2.dilate(base, cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)))

        # Apply operation
        if op_idx == 0:
            result = cv2.dilate(binary, se)
        elif op_idx == 1:
            result = cv2.erode(binary, se)
        elif op_idx == 2:
            result = cv2.morphologyEx(binary, cv2.MORPH_OPEN, se)
        else:
            result = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, se)

        self.current_image = result
        self.morph_in.set_image(binary)
        self.morph_out.set_image(result)
        self.status.showMessage(
            f"🔬  Morfologi '{self.morph_op.currentText()}' "
            f"dengan SE '{self.morph_se.currentText()}' (ukuran {size}) selesai."
        )


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())