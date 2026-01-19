from logger import setup_logger
from engine import (
    build_multi_plan,
    validate_plan,
    execute_plan,
    undo_last_rename,
)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QToolBar,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QFrame,
    QSplitter,
    QHeaderView,
    QMessageBox,
    QStyleOptionButton,
    QStyle,
    QApplication,
)
from PyQt6.QtGui import QAction, QActionGroup, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QSize, QSettings, QTimer, QPropertyAnimation

from core import CATEGORY_MAP, build_name_normal, build_name_advanced


class CheckBoxHeader(QHeaderView):
    def __init__(self, parent=None, window=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.window = window

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        if logicalIndex == 0 and self.window:
            self.window.paint_header_section(painter, rect, logicalIndex)

class NaturalSortItem(QTableWidgetItem):
    def __lt__(self, other):
        import re

        def natural_key(text):
            return [
                int(chunk) if chunk.isdigit() else chunk.lower()
                for chunk in re.split(r"(\d+)", text)
            ]

        return natural_key(self.text()) < natural_key(other.text())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.log = setup_logger()
        self.log.info("Application started")

        self.log = setup_logger().getChild("gui")
        self.log.info("[GUI] MainWindow initialized")


        # High-level window config
        self.setWindowTitle("Batch Renamer")
        self.setMinimumSize(800, 480)

        # Settings for persistence
        self.settings = QSettings("FreshSoft", "BatchRenamer")

        # Core UI setup
        self.setup_widgets()
        self.setup_widget_dicts()
        self.setup_layout()

        # Initial folder state (used by preview)
        self.current_folder = ""

        # Restore window geometry
        geometry = self.settings.value("window_geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)


        # Restore dark mode preference
        dark_enabled = self.settings.value("dark_mode", False, bool)
        self.chk_dark_mode.setChecked(dark_enabled)
        self.apply_dark_mode(dark_enabled)

        # Ctrl+Z to trigger undo
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_undo.activated.connect(self.on_undo_clicked)

        # Drag and drop support
        self.setAcceptDrops(True)

        # Animations
        self._status_anim = None
        self._status_timer = None




    # -------------------------
    # Widget creation
    # -------------------------
    def setup_widgets(self):
        self.log.debug("[GUI] Creating raw widgets")

        # Image Widgets
        self.chk_image_enabled = QCheckBox()
        self.txt_image_prefix = QLineEdit()
        self.txt_image_suffix = QLineEdit()
        self.cmb_image_padding = QComboBox()
        self.cmb_image_padding.addItems(["1", "2", "3", "4"])
        self.spin_image_start = QSpinBox()
        self.spin_image_start.setMinimum(0)
        self.chk_image_advanced = QCheckBox()
        self.txt_image_advanced = QLineEdit()

        # Video Widgets
        self.chk_video_enabled = QCheckBox()
        self.txt_video_prefix = QLineEdit()
        self.txt_video_suffix = QLineEdit()
        self.cmb_video_padding = QComboBox()
        self.cmb_video_padding.addItems(["1", "2", "3", "4"])
        self.spin_video_start = QSpinBox()
        self.spin_video_start.setMinimum(0)
        self.chk_video_advanced = QCheckBox()
        self.txt_video_advanced = QLineEdit()

        # GIF Widgets
        self.chk_gif_enabled = QCheckBox()
        self.txt_gif_prefix = QLineEdit()
        self.txt_gif_suffix = QLineEdit()
        self.cmb_gif_padding = QComboBox()
        self.cmb_gif_padding.addItems(["1", "2", "3", "4"])
        self.spin_gif_start = QSpinBox()
        self.spin_gif_start.setMinimum(0)
        self.chk_gif_advanced = QCheckBox()
        self.txt_gif_advanced = QLineEdit()

        # Audio Widgets
        self.chk_audio_enabled = QCheckBox()
        self.txt_audio_prefix = QLineEdit()
        self.txt_audio_suffix = QLineEdit()
        self.cmb_audio_padding = QComboBox()
        self.cmb_audio_padding.addItems(["1", "2", "3", "4"])
        self.spin_audio_start = QSpinBox()
        self.spin_audio_start.setMinimum(0)
        self.chk_audio_advanced = QCheckBox()
        self.txt_audio_advanced = QLineEdit()

        # Document Widgets
        self.chk_document_enabled = QCheckBox()
        self.txt_document_prefix = QLineEdit()
        self.txt_document_suffix = QLineEdit()
        self.cmb_document_padding = QComboBox()
        self.cmb_document_padding.addItems(["1", "2", "3", "4"])
        self.spin_document_start = QSpinBox()
        self.spin_document_start.setMinimum(0)
        self.chk_document_advanced = QCheckBox()
        self.txt_document_advanced = QLineEdit()

        # Bottom bar widgets
        self.txt_folder = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.chk_recursive = QCheckBox("Recursive")
        self.btn_rename = QPushButton("Rename")

    # -------------------------
    # Widget dictionaries
    # -------------------------
    def setup_widget_dicts(self):

        self.widgets_image = {
            "enabled": self.chk_image_enabled,
            "prefix": self.txt_image_prefix,
            "suffix": self.txt_image_suffix,
            "padding": self.cmb_image_padding,
            "start": self.spin_image_start,
            "advanced_mode": self.chk_image_advanced,
            "advanced_text": self.txt_image_advanced,
        }

        self.widgets_video = {
            "enabled": self.chk_video_enabled,
            "prefix": self.txt_video_prefix,
            "suffix": self.txt_video_suffix,
            "padding": self.cmb_video_padding,
            "start": self.spin_video_start,
            "advanced_mode": self.chk_video_advanced,
            "advanced_text": self.txt_video_advanced,
        }

        self.widgets_gif = {
            "enabled": self.chk_gif_enabled,
            "prefix": self.txt_gif_prefix,
            "suffix": self.txt_gif_suffix,
            "padding": self.cmb_gif_padding,
            "start": self.spin_gif_start,
            "advanced_mode": self.chk_gif_advanced,
            "advanced_text": self.txt_gif_advanced,
        }

        self.widgets_audio = {
            "enabled": self.chk_audio_enabled,
            "prefix": self.txt_audio_prefix,
            "suffix": self.txt_audio_suffix,
            "padding": self.cmb_audio_padding,
            "start": self.spin_audio_start,
            "advanced_mode": self.chk_audio_advanced,
            "advanced_text": self.txt_audio_advanced,
        }

        self.widgets_document = {
            "enabled": self.chk_document_enabled,
            "prefix": self.txt_document_prefix,
            "suffix": self.txt_document_suffix,
            "padding": self.cmb_document_padding,
            "start": self.spin_document_start,
            "advanced_mode": self.chk_document_advanced,
            "advanced_text": self.txt_document_advanced,
        }

        # Unified map for preview logic
        self.widget_dicts = {
            "image": self.widgets_image,
            "video": self.widgets_video,
            "gif": self.widgets_gif,
            "audio": self.widgets_audio,
            "document": self.widgets_document,
        }

    # -------------------------
    # Layout setup
    # -------------------------
    def setup_layout(self):
        self.log.debug("[GUI] Setting up main layout")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # -------------------------
        # Toolbar (left)
        # -------------------------
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.log.debug("[GUI] Building toolbar and category actions")

        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)

        self.action_image = QAction("Image", self, checkable=True)
        self.action_video = QAction("Video", self, checkable=True)
        self.action_gif = QAction("GIF", self, checkable=True)
        self.action_audio = QAction("Audio", self, checkable=True)
        self.action_document = QAction("Document", self, checkable=True)

        for action in [
            self.action_image,
            self.action_video,
            self.action_gif,
            self.action_audio,
            self.action_document,
        ]:
            self.action_group.addAction(action)
            self.toolbar.addAction(action)

        self.action_image.setChecked(True)

        # -------------------------
        # Category pages (center)
        # -------------------------
        self.pages = QStackedWidget()
        self.pages.addWidget(self.build_category_page("image", self.widgets_image))
        self.pages.addWidget(self.build_category_page("video", self.widgets_video))
        self.pages.addWidget(self.build_category_page("gif", self.widgets_gif))
        self.pages.addWidget(self.build_category_page("audio", self.widgets_audio))
        self.pages.addWidget(self.build_category_page("document", self.widgets_document))
        self.log.debug("[GUI] Creating category pages")


        # Toolbar → page switching
        self.action_image.triggered.connect(lambda: self.pages.setCurrentIndex(0))
        self.action_video.triggered.connect(lambda: self.pages.setCurrentIndex(1))
        self.action_gif.triggered.connect(lambda: self.pages.setCurrentIndex(2))
        self.action_audio.triggered.connect(lambda: self.pages.setCurrentIndex(3))
        self.action_document.triggered.connect(lambda: self.pages.setCurrentIndex(4))

        # -------------------------
        # Splitter (settings | preview)
        # -------------------------
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.log.debug("[GUI] Creating splitter and preview container")

        # Left side of splitter = category pages
        self.splitter.addWidget(self.pages)

        # Right side = preview
        self.preview_container = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)
        self.splitter.addWidget(self.preview_container)

        # Restore splitter sizes if available, otherwise use default
        saved_sizes = self.settings.value("splitter_sizes")
        if saved_sizes:
            self.splitter.setSizes([int(x) for x in saved_sizes])
        else:
            self.splitter.setSizes([600, 400])


        # -------------------------
        # Add toolbar + splitter to main layout
        # -------------------------
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)

        top_row.addWidget(self.toolbar)
        top_row.addWidget(self.splitter)

        main_layout.addLayout(top_row)

        # -------------------------
        # Bottom bar
        # -------------------------
        self.bottom_bar = QHBoxLayout()
        self.bottom_bar.setContentsMargins(0, 0, 0, 0)
        self.bottom_bar.setSpacing(10)

        self.bottom_bar.addWidget(QLabel("Folder:"))
        self.bottom_bar.addWidget(self.txt_folder)
        self.bottom_bar.addWidget(self.btn_browse)
        self.bottom_bar.addWidget(self.chk_recursive)
        self.bottom_bar.addStretch()
        self.bottom_bar.addWidget(self.btn_rename)

        # Undo button (always present, disabled until needed)
        self.btn_undo = QPushButton("Undo Last Rename")
        from engine import _undo_stack
        self.btn_undo.setEnabled(len(_undo_stack) > 0)
        self.bottom_bar.addWidget(self.btn_undo)

        main_layout.addLayout(self.bottom_bar)

        # Connect folder browsing
        self.btn_browse.clicked.connect(self.browse_folder)

        # Initialize preview panel and connect signals
        self.init_preview_panel()
        self.connect_preview_signals()

        # Ensure preview panel gets proper space in splitter
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)


        # Wire rename button
        self.log.debug("[GUI] Wiring rename and undo buttons")
        self.wire_rename_button()


    # -------------------------
    # Category Page Builder (C3 style)
    # -------------------------
    def build_category_page(self, category_name, widget_dict):
        self.log.debug(f"[GUI] Building category page: {category_name}")
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # -------------------------
        # Header
        # -------------------------
        header = QLabel(f"{category_name.capitalize()} Settings")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # -------------------------
        # Basic Section
        # -------------------------
        basic_label = QLabel("Basic")
        basic_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(basic_label)

        basic_line = QFrame()
        basic_line.setFrameShape(QFrame.Shape.HLine)
        basic_line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(basic_line)

        self.add_row(layout, "Enabled", widget_dict["enabled"])
        self.add_row(layout, "Prefix", widget_dict["prefix"])
        self.add_row(layout, "Suffix", widget_dict["suffix"])
        self.add_row(layout, "Padding", widget_dict["padding"])
        self.add_row(layout, "Start Number", widget_dict["start"])

        # -------------------------
        # Advanced Section
        # -------------------------
        adv_label = QLabel("Advanced")
        adv_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(adv_label)

        adv_line = QFrame()
        adv_line.setFrameShape(QFrame.Shape.HLine)
        adv_line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(adv_line)

        self.add_row(layout, "Advanced Mode", widget_dict["advanced_mode"])
        self.add_row(layout, "Advanced Text", widget_dict["advanced_text"])

        # Hide advanced text unless advanced mode is checked
        widget_dict["advanced_text"].setVisible(False)
        widget_dict["advanced_mode"].stateChanged.connect(
            lambda state, w=widget_dict["advanced_text"]: w.setVisible(state == Qt.CheckState.Checked)
        )

        layout.addStretch()
        return page

    # -------------------------
    # Helper: Add a labeled row
    # -------------------------
    def add_row(self, parent_layout, label_text, widget):
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setMinimumWidth(110)

        row.addWidget(lbl)
        row.addWidget(widget)
        parent_layout.addLayout(row)

    # -------------------------
    # Preview panel (UI + dark mode)
    # -------------------------
    def init_preview_panel(self):

        self.log.debug("[GUI] Initializing preview panel")


        # Header row: "Preview" + Dark Mode checkbox
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)

        lbl_preview = QLabel("Preview")
        lbl_preview.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.chk_dark_mode = QCheckBox("Dark mode")

        header_row.addWidget(lbl_preview)
        header_row.addStretch()
        header_row.addWidget(self.chk_dark_mode)

        self.preview_layout.addLayout(header_row)

        # Filter row (buttons + category filter)
        filter_row = QHBoxLayout()
        self.log.debug("[GUI] Preview filters initialized")
        filter_row.setContentsMargins(0, 4, 0, 4)
        filter_row.setSpacing(8)

        self.btn_filter_all = QPushButton("Show All")
        self.btn_filter_conflicts = QPushButton("Conflicts Only")
        self.btn_filter_changed = QPushButton("Changed Only")

        filter_row.addWidget(self.btn_filter_all)
        filter_row.addWidget(self.btn_filter_conflicts)
        filter_row.addWidget(self.btn_filter_changed)

        filter_row.addStretch()

        filter_row.addWidget(QLabel("Category:"))
        self.cmb_filter_category = QComboBox()
        self.cmb_filter_category.addItem("All")
        self.cmb_filter_category.addItems(["image", "video", "gif", "audio", "document"])
        filter_row.addWidget(self.cmb_filter_category)

        self.preview_layout.addLayout(filter_row)

        # Preview table
        self.table_preview = QTableWidget()
        self.log.debug("[GUI] Preview table created")
        self.table_preview.setColumnCount(5)
        self.table_preview.setHorizontalHeaderLabels(
            ["", "Category", "Original Name", "New Name", "Conflict"]
        )
        self.table_preview.setSortingEnabled(False)

        # Master checkbox state
        self.master_checked = True

        # Sync row checkboxes → master checkbox
        self.table_preview.itemChanged.connect(self.on_row_checkbox_changed)

        # Override header painting to draw checkbox
        header = CheckBoxHeader(self.table_preview, window=self)
        self.table_preview.setHorizontalHeader(header)

        # Disable sorting indicators entirely
        header.setSortIndicatorShown(False)
        header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)

        # Column 0 must be fixed width
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 28)

        # Other columns resize normally
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Header interaction
        header.setSectionsClickable(True)
        header.setSectionsMovable(False)

        # Handle clicks on header checkbox
        header.sectionClicked.connect(self.on_header_clicked)
        self.log.debug("[GUI] Master checkbox header connected")


        # Block sorting on column 0 at the view level
        self.table_preview.sortItems = self._sort_items_override

        # Enable sorting for other columns
        self.table_preview.setSortingEnabled(True)
        self.log.debug("[GUI] Sorting enabled for preview table")


        self.preview_layout.addWidget(self.table_preview)


        # Status label at bottom
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setObjectName("statusLabel")
        self.lbl_status.setMinimumHeight(32)
        self.lbl_status.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        # Base style – matches your light-mode status style
        self.lbl_status.setStyleSheet(
            "font-size: 13px; padding: 4px 6px; color: gray;"
        )
        self.preview_layout.addWidget(self.lbl_status)

        self.preview_layout.setStretch(0, 0)  # header row
        self.preview_layout.setStretch(1, 0)  # filter row
        self.preview_layout.setStretch(2, 1)  # table expands
        self.preview_layout.setStretch(3, 0)  # status label keeps its height

        # Force layout recalculation for proper sizing
        self.preview_container.updateGeometry()
        self.preview_layout.invalidate()
        self.preview_layout.activate()


        
        # Stretch rules so the table doesn't crush the status bar
        self.preview_layout.setStretch(0, 0)  # header row
        self.preview_layout.setStretch(1, 0)  # filter row
        self.preview_layout.setStretch(2, 1)  # table gets all flexible space
        self.preview_layout.setStretch(3, 0)  # status label keeps its height


        # Dark mode toggle (with persistence)
        def _dark_mode_changed(state):
            enabled = (state == Qt.CheckState.Checked.value)
            self.on_dark_mode_toggled(enabled)

        self.chk_dark_mode.stateChanged.connect(_dark_mode_changed)


        # Filter buttons
        self.btn_filter_all.clicked.connect(self.apply_preview_filters)
        self.btn_filter_conflicts.clicked.connect(self.apply_preview_filters)
        self.btn_filter_changed.clicked.connect(self.apply_preview_filters)
        self.cmb_filter_category.currentIndexChanged.connect(self.apply_preview_filters)
        

    # -------------------------
    # Dark mode styling
    # -------------------------
    def apply_dark_mode(self, enabled: bool):
        if enabled:
            dark = """
            QWidget {
                background-color: #202124;
                color: #E8EAED;
            }
            QLineEdit, QComboBox, QSpinBox, QTableWidget {
                background-color: #303134;
                color: #E8EAED;
                border: 1px solid #5f6368;
            }
            QHeaderView::section {
                background-color: #3c4043;
                color: #E8EAED;
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #3c4043;
                color: #E8EAED;
                border: 1px solid #5f6368;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QToolBar {
                background-color: #202124;
                border: none;
            }
            QLabel#statusLabel {
                background-color: #303134;
                color: #E8EAED;
                font-size: 13px;
                padding: 4px 6px;
            }
            """
            self.setStyleSheet(dark)

        else:
            light = """
            QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit, QComboBox, QSpinBox, QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #C0C0C0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #F0F0F0;
                color: #000000;
                border: 1px solid #C0C0C0;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QToolBar {
                background-color: #FFFFFF;
                border: none;
            }
            QLabel#statusLabel {
                background-color: #F0F0F0;
                color: #444444;
                font-size: 13px;
                padding: 4px 6px;
            }
            """
            self.setStyleSheet(light)
        
            # Force preview layout to recalc AFTER stylesheet is applied
            self.preview_container.updateGeometry()
            self.preview_layout.invalidate()
            self.preview_layout.activate()



    def on_dark_mode_toggled(self, enabled: bool):
        self.apply_dark_mode(enabled)
        self.settings.setValue("dark_mode", enabled)
        self.log.info(f"[GUI] Dark mode toggled | enabled={enabled}")




    def apply_preview_filters(self):
        """
        Apply filters based on:
        - which filter button is 'active'
        - selected category in the combo box
        """
        sender = self.sender()
        mode = "all"

        if sender == self.btn_filter_conflicts:
            mode = "conflicts"
        elif sender == self.btn_filter_changed:
            mode = "changed"
        elif sender == self.btn_filter_all or sender == self.cmb_filter_category:
            mode = "all"

        selected_category = self.cmb_filter_category.currentText()
        self.log.debug(f"[GUI] Applying preview filters | mode={mode} category={selected_category}")


        row_count = self.table_preview.rowCount()
        for row in range(row_count):
            cat_item = self.table_preview.item(row, 1)
            orig_item = self.table_preview.item(row, 2)
            new_item = self.table_preview.item(row, 3)
            conflict_item = self.table_preview.item(row, 4)

            if not (cat_item and orig_item and new_item and conflict_item):
                continue

            cat = cat_item.text()
            orig = orig_item.text()
            new = new_item.text()
            has_conflict = conflict_item.text().strip().lower() == "yes"

            show = True

            # Category filter
            if selected_category != "All" and cat != selected_category:
                show = False

            # Mode filter
            if mode == "conflicts" and not has_conflict:
                show = False
            elif mode == "changed" and orig == new:
                show = False

            self.table_preview.setRowHidden(row, not show)


    # -------------------------
    # Connect signals → preview update
    # -------------------------
    def connect_preview_signals(self):
        """
        Wire up all relevant widgets so that any change triggers a preview refresh.
        The actual logic will live in self.update_preview(), implemented in Chunk 4.
        """

        # Toolbar actions (category changes)
        self.action_image.triggered.connect(self.update_preview)
        self.action_video.triggered.connect(self.update_preview)
        self.action_gif.triggered.connect(self.update_preview)
        self.action_audio.triggered.connect(self.update_preview)
        self.action_document.triggered.connect(self.update_preview)

        # Folder / recursive changes
        self.txt_folder.textChanged.connect(self.update_preview)
        self.chk_recursive.stateChanged.connect(self.update_preview)

        # All category widgets
        for category_key, widget_dict in self.widget_dicts.items():
            self._connect_category_signals(widget_dict)

    def _connect_category_signals(self, widget_dict):
        """
        Connect each widget in a single category to update_preview().
        """
        # enabled: QCheckBox
        widget_dict["enabled"].stateChanged.connect(self.update_preview)

        # prefix / suffix / advanced_text: QLineEdit
        widget_dict["prefix"].textChanged.connect(self.update_preview)
        widget_dict["suffix"].textChanged.connect(self.update_preview)
        widget_dict["advanced_text"].textChanged.connect(self.update_preview)

        # padding: QComboBox
        widget_dict["padding"].currentIndexChanged.connect(self.update_preview)

        # start: QSpinBox
        widget_dict["start"].valueChanged.connect(self.update_preview)

        # advanced_mode: QCheckBox
        widget_dict["advanced_mode"].stateChanged.connect(self.update_preview)

    # -------------------------
    # Folder browsing
    # -------------------------
    def browse_folder(self):
        dialog = QFileDialog(self, "Select folder")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                self.current_folder = selected[0]
                self.log.info(f"[GUI] Folder selected: {self.current_folder}")
                self.txt_folder.setText(self.current_folder)
                self.update_preview()

    # -------------------------
    # Determine active category
    # -------------------------
    def get_active_category_key(self) -> str:
        if self.action_image.isChecked():
            return "image"
        if self.action_video.isChecked():
            return "video"
        if self.action_gif.isChecked():
            return "gif"
        if self.action_audio.isChecked():
            return "audio"
        if self.action_document.isChecked():
            return "document"
        # Fallback
        return "image"

    # -------------------------
    # Build config from widgets
    # -------------------------
    def extract_config(self):
        """
        Build a config dict based on the current state of all widgets.
        This is what renamer_core expects.
        """
        config = {}

        for category_key, widgets in self.widget_dicts.items():
            enabled = widgets["enabled"].isChecked()
            prefix = widgets["prefix"].text()
            suffix = widgets["suffix"].text()
            padding = int(widgets["padding"].currentText())
            start = widgets["start"].value()
            advanced_mode = widgets["advanced_mode"].isChecked()
            advanced_text = widgets["advanced_text"].text()

            config[category_key] = {
                "enabled": enabled,
                "prefix": prefix,
                "suffix": suffix,
                "padding": padding,
                "start": start,
                "advanced_mode": advanced_mode,
                "advanced_text": advanced_text,
            }

        return config

    # -------------------------
    # Preview update logic (multi-category)
    # -------------------------
    def update_preview(self):
        """
        Multi-category preview using the rename engine.
        Shows all enabled categories in one unified table.
        """
        folder = self.txt_folder.text().strip()
        self.current_folder = folder

        # Clear table
        self.table_preview.setRowCount(0)

        if not folder:
            self.set_status("Select a folder to see preview.")
            self.log.info("[GUI] Preview aborted | no folder selected")
            self.btn_rename.setEnabled(False)
            return

        config = self.extract_config()
        recursive = self.chk_recursive.isChecked()
        self.log.debug(f"[GUI] Updating preview | folder='{folder}' recursive={recursive}")


        # Build multi-category plan
        plan = build_multi_plan(
            folder=folder,
            config=config,
            recursive=recursive,
        )

        # If nothing to rename and no conflicts
        if not plan.operations and not plan.conflicts:
            self.set_status("No files found or no changes needed.")
            self.btn_rename.setEnabled(False)
            self.log.info("[GUI] Preview empty | no operations and no conflicts")
            return

        # Validate plan (filesystem conflicts)
        ok, errors = validate_plan(plan)

        # Populate preview table
        for row_index, op in enumerate(plan.operations):
            self.table_preview.insertRow(row_index)
            # Checkbox item
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Checked)
            check_item.setData(Qt.ItemDataRole.UserRole, None)

            item_cat = NaturalSortItem(op.category)
            item_orig = NaturalSortItem(op.old_path.name)
            item_new = NaturalSortItem(op.new_path.name)
            item_conflict = NaturalSortItem("")

            # Detect internal conflicts
            internal_conflict = any(
                f"'{op.new_path.name}'" in msg for msg in plan.conflicts
            )

            # Detect external conflicts
            external_conflict = any(
                op.new_path.as_posix() in msg for msg in errors
            )

            if internal_conflict or external_conflict:
                item_conflict.setText("Yes")
                item_conflict.setForeground(Qt.GlobalColor.red)

                # Highlight entire row
                for col_item in (item_cat, item_orig, item_new, item_conflict):
                    col_item.setBackground(Qt.GlobalColor.yellow)

            self.table_preview.setItem(row_index, 0, check_item)
            self.table_preview.setItem(row_index, 1, item_cat)
            self.table_preview.setItem(row_index, 2, item_orig)
            self.table_preview.setItem(row_index, 3, item_new)
            self.table_preview.setItem(row_index, 4, item_conflict)
            self.log.debug(
                f"[GUI] Row added | row={row_index}old='{op.old_path.name}' new='{op.new_path.name}' "
                f"category='{op.category}' conflict={internal_conflict or external_conflict}"
            )


        # Update status + rename button
        if not ok:
            self.set_status(f"Conflict: {errors[0]}")
            self.log.error(f"[GUI] Preview conflict | first_error='{errors[0]}'")
            self.btn_rename.setEnabled(False)
        else:
            self.set_status(f"Preview ready: {len(plan.operations)} file(s) across enabled categories.")
            self.log.info(f"[GUI] Preview ready | operations={len(plan.operations)} conflicts={len(plan.conflicts)}")
            self.btn_rename.setEnabled(True)

        # Store plan for rename button
        self.current_plan = plan
        self.apply_preview_filters()



    # -------------------------
    # Execute rename (multi-category + undo support)
    # -------------------------
    def perform_rename(self):
        self.log.info("[GUI] Rename requested")
        folder = self.current_folder
        if not folder:
            self.set_status("No folder selected.")
            return

        # Collect checked files
        selected_files = []
        for row in range(self.table_preview.rowCount()):
            item = self.table_preview.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                orig_name = self.table_preview.item(row, 2).text()
                selected_files.append(orig_name)
        self.log.debug(f"[GUI] Selected files for rename: {selected_files}")


        if not selected_files:
            self.set_status("No files selected for renaming.")
            self.log.info("[GUI] Rename aborted | no files selected")
            return

        # Build a filtered plan using only selected files
        plan = build_multi_plan(
            folder=folder,
            config=self.extract_config(),
            recursive=self.chk_recursive.isChecked(),
            selected_files=selected_files
        )

        # Validate before executing
        ok, errors = validate_plan(plan)
        if not ok:
            self.set_status(f"Cannot rename: {errors[0]}")
            self.btn_rename.setEnabled(False)
            self.log.error(f"[GUI] Validation errors: {errors}")
            self.log.error(f"[GUI] Rename blocked | reason={errors[0]}")
            return

        # Show summary dialog
        if not self.show_rename_summary(plan):
            self.set_status("Rename canceled.")
            self.log.info("[GUI] Rename cancelled by user")
            return

        # Execute
        renamed_count, failures = execute_plan(plan)
        self.log.info(f"[GUI] Rename result | renamed={renamed_count} failures={len(failures)}")

        if failures:
            self.set_status(f"Renamed {renamed_count} file(s), {len(failures)} failure(s).")
            self.btn_undo.setEnabled(False)
        else:
            self.set_status(f"Renamed {renamed_count} file(s) successfully.")
            self.btn_undo.setEnabled(True)

        self.update_preview()

    
    # HELPER METHOD: Show rename summary dialogue
    def show_rename_summary(self, plan):
        total_rows = self.table_preview.rowCount()

        selected_files = sum(
            1 for r in range(total_rows)
            if self.table_preview.item(r, 0).checkState() == Qt.CheckState.Checked
        )

        planned_ops = len(plan.operations)

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Rename")
        msg.setIcon(QMessageBox.Icon.Question)

        msg.setText(
            f"<b>Rename {planned_ops} file(s)?</b><br><br>"
            f"Selected: {selected_files} file(s)<br>"
            f"Total in folder: {total_rows} file(s)<br>"
            f"Conflicts: {len(plan.conflicts)}<br>"
        )

        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)

        return msg.exec() == QMessageBox.StandardButton.Yes


    # -------------------------
    # Undo last rename
    # -------------------------
    def on_undo_clicked(self):
        count, errors = undo_last_rename()
        self.log.info(f"[GUI] Undo result | restored={count} errors={errors}")

        # Update status message
        if errors:
            self.set_status(f"Undo failed: {errors[0]}")
            self.log.info("[GUI] Undo requested but no undo available")
        else:
            self.set_status(f"Undo successful: {count} file(s) restored.")

        # Refresh preview so GUI reflects the new filenames
        self.update_preview()

        # Re-enable or disable undo button based on remaining stack
        from engine import _undo_stack
        self.btn_undo.setEnabled(len(_undo_stack) > 0)


    # -------------------------
    # Wire rename + undo buttons
    # -------------------------
    def wire_rename_button(self):
        self.btn_rename.clicked.connect(self.perform_rename)
        self.btn_undo.clicked.connect(self.on_undo_clicked)

        # Create undo button if not created yet
        if not hasattr(self, "btn_undo"):
            self.btn_undo = QPushButton("Undo Last Rename")
            self.btn_undo.setEnabled(False)

            # Add undo button to bottom bar
            parent_layout = self.layout().itemAt(self.layout().count() - 1)
            if isinstance(parent_layout, QHBoxLayout):
                parent_layout.addWidget(self.btn_undo)

    # -------------------------
    # Drag and drop support
    # -------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            folder = urls[0].toLocalFile()
            self.log.info(f"[GUI] Folder dropped: {folder}")
            self.txt_folder.setText(folder)
            self.update_preview()


    # -------------------------
    # Save settings on close
    # -------------------------
    def closeEvent(self, event):
        self.log.debug("[GUI] Saving settings and closing window")

        # Save window geometry
        self.settings.setValue("window_geometry", self.saveGeometry())

        # Save splitter sizes
        self.settings.setValue("splitter_sizes", self.splitter.sizes())

        super().closeEvent(event)


    # --------------------------------
    # Master checkbox helper functions
    # --------------------------------
    def on_row_checkbox_changed(self, item):
        self.log.debug(f"[GUI] Row checkbox changed | row={item.row()} state={item.checkState()}")

        if item.column() != 0:
            return

        total = self.table_preview.rowCount()
        checked = sum(
            1 for r in range(total)
            if self.table_preview.item(r, 0).checkState() == Qt.CheckState.Checked
        )

        # Update master checkbox state
        if checked == total:
            self.master_checked = True
        else:
            self.master_checked = False

        # Repaint header
        self.table_preview.horizontalHeader().viewport().update()
    
    def paint_header_section(self, painter, rect, logicalIndex):
        """
        Draw the master checkbox in the header's first column.
        This is called from wrapped_paint_section in init_preview_panel.
        """
        if logicalIndex != 0:
            return

        opt = QStyleOptionButton()
        opt.rect = rect.adjusted(6, 6, -6, -6)
        opt.state = QStyle.StateFlag.State_Enabled

        if self.master_checked:
            opt.state |= QStyle.StateFlag.State_On
        else:
            opt.state |= QStyle.StateFlag.State_Off

        self.table_preview.style().drawControl(
            QStyle.ControlElement.CE_CheckBox, opt, painter
        )


    def on_header_clicked(self, index):
        # Only respond to clicks on column 0
        if index != 0:
            return

        # Toggle master state
        self.master_checked = not self.master_checked
        self.log.debug(f"[GUI] Master checkbox toggled | new_state={self.master_checked}")


        # Block itemChanged signals to prevent recursion
        self.table_preview.blockSignals(True)

        # Apply the new state to all row checkboxes
        for row in range(self.table_preview.rowCount()):
            item = self.table_preview.item(row, 0)
            if item:
                item.setCheckState(
                    Qt.CheckState.Checked if self.master_checked else Qt.CheckState.Unchecked
                )

        # Re-enable signals
        self.table_preview.blockSignals(False)

        # Repaint header
        self.table_preview.horizontalHeader().viewport().update()


    def _sort_items_override(self, column, order):
        self.log.debug(f"[GUI] Sort override | column={column} order={order}")
        # Completely block sorting on column 0
        if column == 0:
            return

        # Allow normal sorting for other columns
        QTableWidget.sortItems(self.table_preview, column, order)




    # --------------------------------
    # TOAST non-modal messages helper
    # --------------------------------
    #def show_toast(self, message: str, duration_ms: int = 2500):
    #    toast = QLabel(message, self)
    #    toast.setStyleSheet("""
    #        background-color: #323232;
    #        color: white;
    #        border-radius: 6px;
    #    """)
    #    toast.adjustSize()
    #    toast.move(
    #        self.width() - toast.width() - 20,
    #        self.height() - toast.height() - 20
    #    )
    #    toast.show()
    #
    #    # Fade out
    #    toast.setWindowOpacity(1.0)
    #
    #    def fade():
    #        opacity = toast.windowOpacity()
    #        if opacity > 0:
    #            toast.setWindowOpacity(opacity - 0.05)
    #            QTimer.singleShot(30, fade)
    #        else:
    #            toast.deleteLater()
    #
    #    QTimer.singleShot(duration_ms, fade)


    # --------------------------------
    # Status messages
    # --------------------------------
    def set_status(self, text: str, timeout_ms: int = 3000):
        # Stop previous timer
        if self._status_timer:
            self._status_timer.stop()

        # Stop previous animation
        if self._status_anim:
            self._status_anim.stop()

        # Just update content & opacity – no size/style changes
        self.lbl_status.setText(text)
        self.lbl_status.setWindowOpacity(1.0)

        # Auto-clear after timeout
        if timeout_ms > 0:
            self._status_timer = QTimer(self)
            self._status_timer.setSingleShot(True)
            self._status_timer.timeout.connect(self._fade_out_status)
            self._status_timer.start(timeout_ms)


    # Fade-out helper
    def _fade_out_status(self):
        """Fade out the status label smoothly."""
        self._status_anim = QPropertyAnimation(self.lbl_status, b"windowOpacity")
        self._status_anim.setDuration(600)
        self._status_anim.setStartValue(1.0)
        self._status_anim.setEndValue(0.0)
        self._status_anim.finished.connect(lambda: self.lbl_status.setText("Ready"))
        self._status_anim.start()



# -----------------------------------
# For successful Python deployment <3
# ------------------------------------
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
