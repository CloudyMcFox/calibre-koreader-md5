from calibre.gui2.actions import InterfaceAction
from qt.core import QMenu


class KoreaderMD5Action(InterfaceAction):

    name = 'KOReader MD5'
    # (label, icon, tooltip, default_shortcut)
    action_spec = ('KOReader MD5', None,
                   'Compute KOReader partial MD5 hash for selected books', ())
    action_add_menu = True
    action_menu_clone_qaction = True
    action_type = 'current'

    def genesis(self):
        icon = get_icons('images/icon.png', 'KOReader MD5')  # noqa: F821
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.compute_hash)

        # Create a submenu with options
        self.menu = QMenu(self.gui)
        self.qaction.setMenu(self.menu)

        self.compute_action = self.menu.addAction(icon, 'Compute hash for selected books')
        self.compute_action.triggered.connect(self.compute_hash)

        self.menu.addSeparator()
        self.config_action = self.menu.addAction('Configure plugin...')
        self.config_action.triggered.connect(self.show_config)

    def location_selected(self, loc):
        # Enable in both toolbar and context menu
        enabled = loc == 'library'
        self.qaction.setEnabled(enabled)

    def compute_hash(self):
        from calibre_plugins.koreader_md5.main import compute_hashes_for_selected
        compute_hashes_for_selected(self.gui)

    def show_config(self):
        self.interface_action_base_plugin.do_user_config(parent=self.gui)

    def apply_settings(self):
        pass
