from calibre.utils.config import JSONConfig
from qt.core import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

prefs = JSONConfig('plugins/koreader_md5')

# Defaults
prefs.defaults['custom_column'] = ''
prefs.defaults['format_preference'] = 'epub'
prefs.defaults['hash_mode'] = 'exported'  # 'exported' or 'raw'


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        # --- Column selection ---
        col_row = QHBoxLayout()
        self.label = QLabel('Custom &column to store hash:')
        col_row.addWidget(self.label)
        self.column_combo = QComboBox(self)
        col_row.addWidget(self.column_combo)
        self.label.setBuddy(self.column_combo)
        self.l.addLayout(col_row)

        # --- Format preference ---
        fmt_row = QHBoxLayout()
        self.fmt_label = QLabel('Preferred &format:')
        fmt_row.addWidget(self.fmt_label)
        self.fmt_combo = QComboBox(self)
        self.fmt_combo.addItems(['epub', 'mobi', 'azw3', 'pdf', 'cbz', 'cbr', 'fb2', 'djvu'])
        current_fmt = prefs['format_preference']
        idx = self.fmt_combo.findText(current_fmt)
        if idx >= 0:
            self.fmt_combo.setCurrentIndex(idx)
        fmt_row.addWidget(self.fmt_combo)
        self.fmt_label.setBuddy(self.fmt_combo)
        self.l.addLayout(fmt_row)

        # --- Hash mode ---
        mode_row = QHBoxLayout()
        self.mode_label = QLabel('Hash &mode:')
        mode_row.addWidget(self.mode_label)
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItem(
            'Exported (recommended) — use if you send to device from calibre or calibre web',
            'exported'
        )
        self.mode_combo.addItem(
            'Raw — use if you sideload the unchanged epub directly',
            'raw'
        )
        current_mode = prefs['hash_mode']
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == current_mode:
                self.mode_combo.setCurrentIndex(i)
                break
        mode_row.addWidget(self.mode_combo)
        self.mode_label.setBuddy(self.mode_combo)
        self.l.addLayout(mode_row)

        # --- Info label ---
        info = QLabel(
            '<small><b>Exported</b>: Embeds current metadata into a temp copy before hashing. '
            'Use this if you send books to your device from calibre or calibre web.<br>'
            '<b>Raw</b>: Hashes the file as-is from the library with no modification. '
            'Use this if you sideload the unchanged epub directly to your device.</small>'
        )
        info.setWordWrap(True)
        self.l.addWidget(info)

        # Populate columns
        self._populate_columns()

    def _populate_columns(self):
        from calibre.gui2.ui import get_gui
        gui = get_gui()
        if gui is None:
            return
        db = gui.current_db
        custom_columns = db.field_metadata.custom_field_metadata()
        current = prefs['custom_column']
        selected_idx = 0
        for i, (key, meta) in enumerate(sorted(custom_columns.items())):
            if meta.get('datatype') in ('text', 'comments'):
                label = meta.get('name', key)
                self.column_combo.addItem(f'{label} ({key})', key)
                if key == current:
                    selected_idx = self.column_combo.count() - 1
        if self.column_combo.count() > 0:
            self.column_combo.setCurrentIndex(selected_idx)

    def save_settings(self):
        idx = self.column_combo.currentIndex()
        if idx >= 0:
            prefs['custom_column'] = self.column_combo.itemData(idx)
        prefs['format_preference'] = self.fmt_combo.currentText()
        prefs['hash_mode'] = self.mode_combo.currentData()
