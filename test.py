import sys, cv2, numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTabWidget, QGroupBox,
    QGridLayout, QComboBox, QSlider, QSpinBox, QStatusBar,
    QSplitter, QFrame, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ── THEME ──────────────────────────────────────────────────────────
BG      = "#07090f"
BG2     = "#0d1117"
BG3     = "#111827"
BG4     = "#0f1520"
BORDER  = "#1a2236"
ACC     = "#6c63ff"
ACC2    = "#00d4ff"
ACC3    = "#ff6584"
GRN     = "#00e5a0"
YLW     = "#ffb347"
TXT     = "#e8eaf0"
TXT2    = "#6b7a99"
TXT3    = "#3a4460"

STYLE = f"""
QMainWindow, QWidget {{ background:{BG2}; color:{TXT}; font-family:'Segoe UI',Arial,sans-serif; font-size:12px; }}
QTabWidget::pane {{ border:1px solid {BORDER}; background:{BG3}; border-radius:0 0 10px 10px; }}
QTabBar {{ background:{BG4}; }}
QTabBar::tab {{ background:transparent; color:{TXT2}; padding:11px 18px; border:none; border-bottom:3px solid transparent; font-size:12px; font-weight:500; min-width:120px; }}
QTabBar::tab:selected {{ color:{ACC2}; border-bottom:3px solid {ACC2}; background:{BG3}; }}
QTabBar::tab:hover:!selected {{ color:{TXT}; background:rgba(108,99,255,0.07); }}
QGroupBox {{ border:1px solid {BORDER}; border-radius:10px; margin-top:16px; padding:14px 10px 10px 10px; background:{BG4}; }}
QGroupBox::title {{ subcontrol-origin:margin; left:14px; padding:0 6px; color:{ACC}; font-weight:600; font-size:11px; letter-spacing:1px; }}
QComboBox {{ background:{BG2}; color:{TXT}; border:1px solid {BORDER}; border-radius:8px; padding:7px 12px; font-size:12px; }}
QComboBox:hover {{ border-color:{ACC}; }}
QComboBox::drop-down {{ border:none; width:24px; }}
QComboBox QAbstractItemView {{ background:{BG3}; color:{TXT}; border:1px solid {BORDER}; selection-background-color:{ACC}; border-radius:8px; padding:4px; }}
QSlider::groove:horizontal {{ background:{BG2}; height:6px; border-radius:3px; }}
QSlider::handle:horizontal {{ background:{ACC}; width:16px; height:16px; border-radius:8px; margin:-5px 0; border:2px solid {BG3}; }}
QSlider::sub-page:horizontal {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC},stop:1 {ACC2}); border-radius:3px; }}
QSpinBox {{ background:{BG2}; color:{TXT}; border:1px solid {BORDER}; border-radius:8px; padding:6px 10px; }}
QSpinBox:hover {{ border-color:{ACC}; }}
QScrollArea, QScrollBar {{ border:none; background:transparent; }}
QScrollBar:vertical {{ width:6px; background:transparent; }}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QStatusBar {{ background:{BG}; color:{TXT2}; border-top:1px solid {BORDER}; padding:4px 12px; font-size:11px; }}
QSplitter::handle {{ background:{BORDER}; }}
"""

def glow_btn(text, grad, parent=None):
    b = QPushButton(text, parent)
    b.setFixedHeight(38)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{ background:{grad}; color:white; border:none; border-radius:9px; padding:0 20px; font-weight:700; font-size:12px; }}
        QPushButton:hover {{ opacity:0.9; }}
        QPushButton:pressed {{ opacity:0.7; }}
    """)
    return b

def outline_btn(text, color=ACC, parent=None):
    b = QPushButton(text, parent)
    b.setFixedHeight(36)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{ background:transparent; color:{color}; border:1.5px solid {color}; border-radius:9px; padding:0 16px; font-weight:600; }}
        QPushButton:hover {{ background:{color}; color:white; }}
        QPushButton:pressed {{ opacity:0.7; }}
    """)
    return b

def badge(text, color=ACC):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        QLabel {{ background:{color}22; color:{color}; border:1px solid {color}55;
                  border-radius:10px; padding:2px 10px; font-size:10px; font-weight:700; }}
    """)
    lbl.setFixedHeight(22)
    return lbl

def divider():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
    return f

def section_title(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{TXT}; font-size:14px; font-weight:700; padding-bottom:6px; border-bottom:2px solid {ACC}; margin-bottom:8px;")
    return lbl

class ImagePanel(QLabel):
    def __init__(self, ph="Gambar akan tampil di sini"):
        super().__init__()
        self._ph = ph
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(280, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._empty()

    def _empty(self):
        self.setText(f'<div style="text-align:center;"><div style="font-size:28px;margin-bottom:6px;">🖼</div><div style="color:{TXT3};font-size:11px;">{self._ph}</div></div>')
        self.setStyleSheet(f"QLabel {{ background:{BG4}; border:2px dashed {BORDER}; border-radius:12px; color:{TXT3}; }}")

    def set_image(self, img):
        if img is None:
            self._empty(); return
        if len(img.shape) == 2:
            h, w = img.shape
            qi = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        else:
            h, w, c = img.shape
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qi = QImage(rgb.data, w, h, w*c, QImage.Format_RGB888)
        px = QPixmap.fromImage(qi).scaled(self.width()-16, self.height()-16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(px)
        self.setStyleSheet(f"QLabel {{ background:{BG4}; border:2px solid {ACC}66; border-radius:12px; }}")

class HistCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(7,3.2), facecolor=BG4)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def plot(self, img):
        self.fig.clear()
        ax = self.fig.add_subplot(111, facecolor=BG2)
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=TXT2, labelsize=8)
        ax.set_xlim([0,256])
        ax.set_xlabel('Intensitas Piksel', color=TXT2, fontsize=9)
        ax.set_ylabel('Frekuensi', color=TXT2, fontsize=9)
        if len(img.shape) == 2:
            h = cv2.calcHist([img],[0],None,[256],[0,256]).flatten()
            ax.fill_between(range(256), h, alpha=0.5, color=ACC)
            ax.plot(h, color=ACC, linewidth=1.4)
            ax.set_title('Histogram — Grayscale', color=TXT, fontsize=11, fontweight='bold', pad=10)
        else:
            for idx, col, lbl in [(0,ACC2,'Blue'),(1,GRN,'Green'),(2,ACC3,'Red')]:
                h = cv2.calcHist([img],[idx],None,[256],[0,256]).flatten()
                ax.fill_between(range(256), h, alpha=0.18, color=col)
                ax.plot(h, color=col, linewidth=1.4, label=lbl)
            ax.set_title('Histogram — RGB', color=TXT, fontsize=11, fontweight='bold', pad=10)
            leg = ax.legend(facecolor=BG3, edgecolor=BORDER, fontsize=9)
            [t.set_color(TXT) for t in leg.get_texts()]
        self.fig.tight_layout(pad=1.5)
        self.draw()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.orig = None
        self.curr = None
        self._ui()

    def _ui(self):
        self.setWindowTitle("CitraLab  ·  Pengolahan Citra Digital  ·  IK24")
        self.setMinimumSize(1160, 740)
        self.setStyleSheet(STYLE)
        self.sb = QStatusBar(); self.setStatusBar(self.sb)
        self.sb.showMessage("✨  Selamat datang di CitraLab! Klik Buka Gambar untuk memulai.")

        root = QWidget(); self.setCentralWidget(root)
        vl = QVBoxLayout(root); vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        vl.addWidget(self._header())

        sp = QSplitter(Qt.Horizontal)
        sp.addWidget(self._sidebar())
        sp.addWidget(self._tabs())
        sp.setSizes([272, 888]); sp.setHandleWidth(2)
        vl.addWidget(sp, 1)

    def _header(self):
        bar = QFrame(); bar.setFixedHeight(62)
        bar.setStyleSheet(f"QFrame {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {BG},stop:0.5 #0e1628,stop:1 {BG}); border-bottom:1px solid {BORDER}; }}")
        hl = QHBoxLayout(bar); hl.setContentsMargins(20,0,20,0); hl.setSpacing(12)

        icon = QLabel("◈")
        icon.setStyleSheet(f"font-size:24px; color:{ACC}; padding:0;")
        title = QLabel("CitraLab")
        title.setStyleSheet(f"font-size:20px; font-weight:800; color:{TXT}; letter-spacing:1px;")
        sub = QLabel("Pengolahan Citra Digital · IK24")
        sub.setStyleSheet(f"font-size:11px; color:{TXT2}; margin-left:6px;")
        hl.addWidget(icon); hl.addWidget(title); hl.addWidget(sub); hl.addStretch()

        GRAD_OPEN  = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC},stop:1 {ACC2})"
        GRAD_SAVE  = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00c9a7,stop:1 {GRN})"
        GRAD_RESET = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC3},stop:1 #ff4757)"

        b1 = glow_btn("  📂  Buka Gambar", GRAD_OPEN); b1.setMinimumWidth(150); b1.clicked.connect(self.open_img)
        b2 = glow_btn("  💾  Simpan", GRAD_SAVE); b2.setMinimumWidth(120); b2.clicked.connect(self.save_img)
        b3 = glow_btn("  ↺  Reset", GRAD_RESET); b3.setMinimumWidth(100); b3.clicked.connect(self.reset_img)
        for b in [b1, b2, b3]: hl.addWidget(b)
        return bar

    def _sidebar(self):
        w = QWidget(); w.setFixedWidth(268)
        w.setStyleSheet(f"background:{BG4}; border-right:1px solid {BORDER};")
        vl = QVBoxLayout(w); vl.setContentsMargins(14,16,14,16); vl.setSpacing(12)

        # Preview card
        pc = QFrame(); pc.setStyleSheet(f"QFrame {{ background:{BG3}; border:1px solid {BORDER}; border-radius:12px; }}")
        pl = QVBoxLayout(pc); pl.setContentsMargins(10,10,10,10); pl.setSpacing(8)
        ph = QHBoxLayout()
        pt = QLabel("Preview Asli"); pt.setStyleSheet(f"font-weight:700; font-size:11px; color:{TXT2}; text-transform:uppercase; letter-spacing:1px;")
        self.pv_badge = badge("No Image", TXT3)
        ph.addWidget(pt); ph.addStretch(); ph.addWidget(self.pv_badge)
        pl.addLayout(ph)
        self.pv = QLabel("Belum ada gambar"); self.pv.setAlignment(Qt.AlignCenter)
        self.pv.setFixedHeight(175)
        self.pv.setStyleSheet(f"background:{BG}; border-radius:8px; color:{TXT3}; font-size:11px;")
        pl.addWidget(self.pv); vl.addWidget(pc)

        # Info card
        ic = QFrame(); ic.setStyleSheet(f"QFrame {{ background:{BG3}; border:1px solid {BORDER}; border-radius:12px; }}")
        il = QVBoxLayout(ic); il.setContentsMargins(12,12,12,12)
        it = QLabel("ℹ  Info Gambar"); it.setStyleSheet(f"font-weight:700; font-size:11px; color:{TXT2}; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;")
        il.addWidget(it)
        self.info = QLabel("—"); self.info.setStyleSheet(f"font-size:11px; color:{TXT2}; line-height:1.8;"); self.info.setWordWrap(True)
        il.addWidget(self.info); vl.addWidget(ic)

        # Points card
        pts = QFrame(); pts.setStyleSheet(f"QFrame {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1a1040,stop:1 #0d1a30); border:1px solid {ACC}44; border-radius:12px; }}")
        ptl = QVBoxLayout(pts); ptl.setContentsMargins(12,12,12,12); ptl.setSpacing(6)
        ptt = QLabel("🏆  Poin Fitur"); ptt.setStyleSheet(f"font-weight:700; font-size:11px; color:{ACC}; text-transform:uppercase; letter-spacing:1px;")
        ptl.addWidget(ptt)
        for lbl, pts_txt, col in [("Fitur Wajib","40 poin",GRN),("Histogram","10 poin",ACC2),("Konvolusi/Filter","20 poin",YLW),("Morfologi","30 poin",ACC3)]:
            rw = QHBoxLayout()
            lb = QLabel(f"· {lbl}"); lb.setStyleSheet(f"font-size:11px; color:{TXT2};")
            bg = badge(pts_txt, col)
            rw.addWidget(lb); rw.addStretch(); rw.addWidget(bg); ptl.addLayout(rw)
        ptl.addWidget(divider())
        tr = QHBoxLayout()
        tl = QLabel("Total Maksimal"); tl.setStyleSheet(f"font-size:12px; font-weight:700; color:{TXT};")
        tb = badge("100 poin", ACC)
        tr.addWidget(tl); tr.addStretch(); tr.addWidget(tb); ptl.addLayout(tr)
        vl.addWidget(pts); vl.addStretch()
        return w

    def _tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_display(),   "🖼  Tampilkan")
        self.tabs.addTab(self._tab_basic(),     "⚙  Proses Dasar")
        self.tabs.addTab(self._tab_arith(),     "➕  Aritmatika & Logika")
        self.tabs.addTab(self._tab_hist(),      "📊  Histogram")
        self.tabs.addTab(self._tab_conv(),      "🔍  Konvolusi / Filter")
        self.tabs.addTab(self._tab_morph(),     "🔬  Morfologi")
        return self.tabs

    def _wrap(self, inner, title=""):
        outer = QWidget()
        vl = QVBoxLayout(outer); vl.setContentsMargins(20,18,20,18); vl.setSpacing(14)
        if title: vl.addWidget(section_title(title))
        vl.addWidget(inner, 1)
        return outer

    def _io_panels(self, a_in, a_out, la="Input", lb="Output"):
        w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0,0,0,0); hl.setSpacing(12)
        for tag, attr in [(la, a_in), (lb, a_out)]:
            bx = QVBoxLayout()
            th = QHBoxLayout()
            t = QLabel(tag); t.setStyleSheet(f"font-size:11px; font-weight:600; color:{TXT2}; text-transform:uppercase; letter-spacing:1px;")
            th.addWidget(t); th.addStretch(); bx.addLayout(th)
            p = ImagePanel(f"— {tag} —"); setattr(self, attr, p); bx.addWidget(p, 1); hl.addLayout(bx)
        return w

    def _tab_display(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0)
        self.disp = ImagePanel("Buka gambar untuk menampilkan"); vl.addWidget(self.disp, 1)
        return self._wrap(inner, "🖼  Tampilkan Gambar Asli")

    def _tab_basic(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0); vl.setSpacing(12)
        grp = QGroupBox("Kontrol Proses"); cl = QGridLayout(grp); cl.setSpacing(10)
        bg = outline_btn("🌑  Grayscale", ACC2); bg.clicked.connect(self.to_gray); bg.setMinimumWidth(160)
        bb = outline_btn("⬛  Citra Biner", ACC); bb.clicked.connect(self.to_bin); bb.setMinimumWidth(160)
        tl = QLabel("Threshold Biner:"); tl.setStyleSheet(f"color:{TXT2}; font-size:11px;")
        self.tslider = QSlider(Qt.Horizontal); self.tslider.setRange(0,255); self.tslider.setValue(127)
        self.tval = QLabel("127"); self.tval.setStyleSheet(f"color:{ACC}; font-weight:700; min-width:30px;")
        self.tslider.valueChanged.connect(lambda v: self.tval.setText(str(v)))
        cl.addWidget(bg,0,0); cl.addWidget(bb,0,1); cl.addWidget(tl,1,0); cl.addWidget(self.tslider,1,1); cl.addWidget(self.tval,1,2)
        vl.addWidget(grp); vl.addWidget(self._io_panels("basic_in","basic_out"), 1)
        return self._wrap(inner, "⚙  Proses Dasar")

    def _tab_arith(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0); vl.setSpacing(12)
        GRAD_A = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC},stop:1 {ACC2})"
        GRAD_L = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00c9a7,stop:1 {GRN})"
        ga = QGroupBox("Operasi Aritmatika"); al = QHBoxLayout(ga); al.setSpacing(10)
        self.acmb = QComboBox(); self.acmb.addItems(["Penjumlahan (Add)","Pengurangan (Subtract)","Perkalian (Multiply)","Pembagian (Divide)"])
        self.aspin = QSpinBox(); self.aspin.setRange(0,255); self.aspin.setValue(50); self.aspin.setPrefix("Nilai: ")
        ba = glow_btn("▶  Jalankan", GRAD_A); ba.setMinimumWidth(130); ba.clicked.connect(self.do_arith)
        al.addWidget(self.acmb,3); al.addWidget(self.aspin,1); al.addWidget(ba); vl.addWidget(ga)

        gl = QGroupBox("Operasi Logika"); ll = QHBoxLayout(gl); ll.setSpacing(10)
        self.lcmb = QComboBox(); self.lcmb.addItems(["AND","OR","NOT","XOR"])
        bl = glow_btn("▶  Jalankan", GRAD_L); bl.setMinimumWidth(130); bl.clicked.connect(self.do_logic)
        ll.addWidget(self.lcmb,2); ll.addWidget(bl); vl.addWidget(gl)
        vl.addWidget(self._io_panels("arith_in","arith_out"), 1)
        return self._wrap(inner, "➕  Aritmatika & Logika")

    def _tab_hist(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0); vl.setSpacing(12)
        GRAD_H = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC},stop:1 {ACC2})"
        top = QHBoxLayout()
        bh = glow_btn("📊  Tampilkan Histogram", GRAD_H); bh.setMinimumWidth(200); bh.clicked.connect(self.do_hist)
        top.addWidget(bh); top.addStretch(); vl.addLayout(top)
        self.hcanvas = HistCanvas(); self.hcanvas.setMinimumHeight(260); vl.addWidget(self.hcanvas, 2)
        self.himg = ImagePanel("Gambar yang dianalisis"); self.himg.setMaximumHeight(200); vl.addWidget(self.himg, 1)
        return self._wrap(inner, "📊  Analisis Histogram")

    def _tab_conv(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0); vl.setSpacing(12)
        GRAD_C = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC},stop:1 {ACC2})"
        grp = QGroupBox("Pengaturan Filter Konvolusi"); gl = QHBoxLayout(grp); gl.setSpacing(10)
        self.ccmb = QComboBox(); self.ccmb.addItems(["Gaussian Blur (Smoothing)","Sharpening (Ketajaman)","Edge Detection — Sobel","Edge Detection — Laplacian","Emboss Effect"])
        self.cksz = QSpinBox(); self.cksz.setRange(3,21); self.cksz.setSingleStep(2); self.cksz.setValue(5); self.cksz.setPrefix("Kernel: ")
        bc = glow_btn("▶  Terapkan Filter", GRAD_C); bc.setMinimumWidth(150); bc.clicked.connect(self.do_conv)
        gl.addWidget(self.ccmb,3); gl.addWidget(self.cksz,1); gl.addWidget(bc); vl.addWidget(grp)
        vl.addWidget(self._io_panels("conv_in","conv_out"), 1)
        return self._wrap(inner, "🔍  Konvolusi & Filter")

    def _tab_morph(self):
        inner = QWidget(); vl = QVBoxLayout(inner); vl.setContentsMargins(0,0,0,0); vl.setSpacing(12)
        GRAD_M = f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACC3},stop:1 #ff4757)"
        grp = QGroupBox("Parameter Morfologi"); gl = QGridLayout(grp); gl.setSpacing(10); gl.setColumnStretch(1,2)
        for i, t in enumerate(["Operasi:","Elemen Penstruktur (SE):","Ukuran SE:"]):
            lb = QLabel(t); lb.setStyleSheet(f"color:{TXT2}; font-size:11px;"); gl.addWidget(lb,i,0)
        self.mop = QComboBox(); self.mop.addItems(["Dilasi","Erosi","Opening (Erosi → Dilasi)","Closing (Dilasi → Erosi)"])
        self.mse = QComboBox(); self.mse.addItems(["Persegi (Rectangle)","Ellipse","Cross (Plus)","Diamond"])
        self.msz = QSpinBox(); self.msz.setRange(3,21); self.msz.setSingleStep(2); self.msz.setValue(5)
        bm = glow_btn("▶  Terapkan Morfologi", GRAD_M); bm.setMinimumWidth(180); bm.clicked.connect(self.do_morph)
        gl.addWidget(self.mop,0,1); gl.addWidget(self.mse,1,1); gl.addWidget(self.msz,2,1); gl.addWidget(bm,3,0,1,2)
        vl.addWidget(grp); vl.addWidget(self._io_panels("morph_in","morph_out","Input (Binary)","Output"), 1)
        return self._wrap(inner, "🔬  Operasi Morfologi")

    # ── Actions ────────────────────────────────────────
    def open_img(self):
        p, _ = QFileDialog.getOpenFileName(self,"Buka Gambar","","Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")
        if not p: return
        img = cv2.imread(p)
        if img is None: QMessageBox.critical(self,"Error","Gagal membuka gambar!"); return
        self.orig = img; self.curr = img.copy()
        self.disp.set_image(img); self.basic_in.set_image(img); self.arith_in.set_image(img); self.conv_in.set_image(img)
        h,w = img.shape[:2]; ch = img.shape[2] if len(img.shape)==3 else 1; fname = p.replace("\\","/").split("/")[-1]
        self.info.setText(f"<b style='color:{TXT}'>Ukuran:</b> {w}×{h} px<br><b style='color:{TXT}'>Channel:</b> {ch}<br><b style='color:{TXT}'>Tipe:</b> {img.dtype}<br><b style='color:{TXT}'>File:</b> {fname}")
        self.pv_badge.setText("Loaded ✓"); self.pv_badge.setStyleSheet(f"QLabel {{ background:{GRN}22; color:{GRN}; border:1px solid {GRN}55; border-radius:10px; padding:2px 10px; font-size:10px; font-weight:700; }}")
        if len(img.shape)==2: qi = QImage(img.data,w,h,w,QImage.Format_Grayscale8)
        else: rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB); qi = QImage(rgb.data,w,h,w*ch,QImage.Format_RGB888)
        self.pv.setPixmap(QPixmap.fromImage(qi).scaled(240,170,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.pv.setStyleSheet(f"background:{BG}; border-radius:8px;")
        self.sb.showMessage(f"✅  Gambar dimuat: {p}")

    def save_img(self):
        if self.curr is None: QMessageBox.warning(self,"Peringatan","Tidak ada gambar!"); return
        p, _ = QFileDialog.getSaveFileName(self,"Simpan","hasil_proses.png","PNG (*.png);;JPG (*.jpg)")
        if p: cv2.imwrite(p, self.curr); self.sb.showMessage(f"💾  Disimpan: {p}")

    def reset_img(self):
        if self.orig is None: return
        self.curr = self.orig.copy()
        self.disp.set_image(self.orig); self.basic_in.set_image(self.orig); self.arith_in.set_image(self.orig); self.conv_in.set_image(self.orig)
        for a in ["basic_out","arith_out","conv_out","morph_in","morph_out"]: getattr(self,a).set_image(None)
        self.sb.showMessage("🔄  Direset ke gambar asli.")

    def _chk(self):
        if self.orig is None: QMessageBox.warning(self,"Peringatan","Buka gambar dulu!"); return False
        return True

    def to_gray(self):
        if not self._chk(): return
        g = cv2.cvtColor(self.orig, cv2.COLOR_BGR2GRAY); self.curr=g; self.basic_out.set_image(g); self.sb.showMessage("⚙  Grayscale selesai.")

    def to_bin(self):
        if not self._chk(): return
        g = cv2.cvtColor(self.orig, cv2.COLOR_BGR2GRAY); t=self.tslider.value()
        _, bw = cv2.threshold(g,t,255,cv2.THRESH_BINARY); self.curr=bw; self.basic_out.set_image(bw); self.sb.showMessage(f"⚙  Biner (t={t}) selesai.")

    def do_arith(self):
        if not self._chk(): return
        img=self.orig.astype(np.float32); v=self.aspin.value(); op=self.acmb.currentIndex()
        sc=np.full_like(img,v,dtype=np.float32)
        if op==0: r=cv2.add(img,sc)
        elif op==1: r=cv2.subtract(img,sc)
        elif op==2: r=img*(v/50.0)
        else: r=img/max(v,1)
        r=np.clip(r,0,255).astype(np.uint8); self.curr=r; self.arith_in.set_image(self.orig); self.arith_out.set_image(r)
        self.sb.showMessage(f"➕  Aritmatika '{self.acmb.currentText()}' selesai.")

    def do_logic(self):
        if not self._chk(): return
        g=cv2.cvtColor(self.orig,cv2.COLOR_BGR2GRAY); _,bw=cv2.threshold(g,127,255,cv2.THRESH_BINARY)
        mask=np.full_like(bw,128); op=self.lcmb.currentText()
        if op=="AND": r=cv2.bitwise_and(bw,mask)
        elif op=="OR": r=cv2.bitwise_or(bw,mask)
        elif op=="NOT": r=cv2.bitwise_not(bw)
        else: r=cv2.bitwise_xor(bw,mask)
        self.curr=r; self.arith_in.set_image(self.orig); self.arith_out.set_image(r); self.sb.showMessage(f"🔣  Logika '{op}' selesai.")

    def do_hist(self):
        if not self._chk(): return
        self.hcanvas.plot(self.orig); self.himg.set_image(self.orig); self.sb.showMessage("📊  Histogram ditampilkan.")

    def do_conv(self):
        if not self._chk(): return
        img=self.orig; k=self.cksz.value()
        if k%2==0: k+=1
        op=self.ccmb.currentIndex()
        if op==0: r=cv2.GaussianBlur(img,(k,k),0)
        elif op==1: r=cv2.filter2D(img,-1,np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]))
        elif op==2:
            g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); sx=cv2.Sobel(g,cv2.CV_64F,1,0,ksize=k); sy=cv2.Sobel(g,cv2.CV_64F,0,1,ksize=k)
            r=cv2.convertScaleAbs(cv2.magnitude(sx,sy))
        elif op==3:
            g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); r=cv2.convertScaleAbs(cv2.Laplacian(g,cv2.CV_64F,ksize=k))
        else: r=cv2.filter2D(img,-1,np.array([[-2,-1,0],[-1,1,1],[0,1,2]]))
        self.curr=r; self.conv_in.set_image(img); self.conv_out.set_image(r); self.sb.showMessage(f"🔍  Filter '{self.ccmb.currentText()}' diterapkan.")

    def do_morph(self):
        if not self._chk(): return
        g=cv2.cvtColor(self.orig,cv2.COLOR_BGR2GRAY); _,bw=cv2.threshold(g,127,255,cv2.THRESH_BINARY)
        sz=self.msz.value(); si=self.mse.currentIndex(); oi=self.mop.currentIndex()
        if si==0: se=cv2.getStructuringElement(cv2.MORPH_RECT,(sz,sz))
        elif si==1: se=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(sz,sz))
        elif si==2: se=cv2.getStructuringElement(cv2.MORPH_CROSS,(sz,sz))
        else:
            b=cv2.getStructuringElement(cv2.MORPH_CROSS,(sz,sz)); se=cv2.dilate(b,cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)))
        if oi==0: r=cv2.dilate(bw,se)
        elif oi==1: r=cv2.erode(bw,se)
        elif oi==2: r=cv2.morphologyEx(bw,cv2.MORPH_OPEN,se)
        else: r=cv2.morphologyEx(bw,cv2.MORPH_CLOSE,se)
        self.curr=r; self.morph_in.set_image(bw); self.morph_out.set_image(r)
        self.sb.showMessage(f"🔬  Morfologi '{self.mop.currentText()}' | SE '{self.mse.currentText()}' ukuran {sz} selesai.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = App(); w.show()
    sys.exit(app.exec_())