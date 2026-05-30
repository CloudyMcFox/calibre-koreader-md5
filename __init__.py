from calibre.customize import InterfaceActionBase


class KoreaderMD5Plugin(InterfaceActionBase):
    '''
    Plugin that computes a partial MD5 hash (compatible with KOReader's
    partial_md5 algorithm) for book files and stores the result in a
    user-configured custom column.
    '''

    name = 'KOReader MD5'
    description = 'Compute KOReader-compatible partial MD5 hash and store in a custom column'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'CloudyMcFox'
    version = (1, 0, 0)
    minimum_calibre_version = (5, 0, 0)

    actual_plugin = 'calibre_plugins.koreader_md5.ui:KoreaderMD5Action'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.koreader_md5.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
