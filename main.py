import hashlib
import os
import tempfile

from calibre_plugins.koreader_md5.config import prefs


def partial_md5(path):
    '''
    Compute a partial MD5 hash compatible with KOReader's algorithm.

    Reads 1024-byte chunks at exponentially increasing offsets:
        offset = 1024 << (2 * i)  for i in range(-1, 11)

    This samples the file sparsely, making it fast for large files while
    still producing a reasonably unique fingerprint.
    '''
    if not path:
        return ''

    try:
        f = open(path, 'rb')
    except OSError:
        return ''

    try:
        md5 = hashlib.md5()
        buf_size = 1024

        for i in range(-1, 11):
            shift = 2 * i
            if shift < 0:
                # In Go, uint(-2) wraps to a huge value, shift >= 64 gives 0
                offset = 0
            else:
                offset = 1024 << shift
            f.seek(offset)
            buf = f.read(buf_size)
            if not buf:
                break
            md5.update(buf)

        return md5.hexdigest()
    except OSError:
        return ''
    finally:
        f.close()


def hash_raw(db, book_id, fmt):
    '''
    Hash the file exactly as stored in calibre's library, without
    any metadata re-embedding. Use this if you sideload books to
    KOReader without going through calibre's "Send to device".
    '''
    fmt_data = db.format(book_id, fmt)
    if fmt_data is None:
        return ''

    tmp_path = None
    try:
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=f'.{fmt.lower()}', prefix='koreader_md5_'
        )
        tmp.write(fmt_data)
        tmp.close()
        tmp_path = tmp.name
        return partial_md5(tmp_path)
    except Exception:
        return ''
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def export_and_hash(db, book_id, fmt):
    '''
    Export the book to a temp file using calibre's save-to-disk logic
    (which mirrors what "Send to device" produces), then hash that file.

    This ensures the hash matches what KOReader computes on the device,
    because calibre modifies epub metadata in its internal library copy.
    '''
    from calibre.ebooks.metadata.meta import set_metadata, get_metadata
    from calibre.library.save_to_disk import config as save_config

    # Get the raw format bytes from the library
    fmt_data = db.format(book_id, fmt)
    if fmt_data is None:
        return ''

    tmp_path = None
    try:
        # Write to temp file
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=f'.{fmt.lower()}', prefix='koreader_md5_'
        )
        tmp.write(fmt_data)
        tmp.close()
        tmp_path = tmp.name

        # Apply metadata to the temp file — this replicates what calibre does
        # when sending to device (it embeds current metadata into the file).
        # This produces the same bytes KOReader will see on the device.
        mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
        with open(tmp_path, 'r+b') as f:
            set_metadata(f, mi, fmt.lower())

        # Now hash the exported file
        return partial_md5(tmp_path)
    except Exception:
        return ''
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def compute_hashes_for_selected(gui):
    '''
    Compute partial MD5 hashes for all selected books and store
    the result in the configured custom column.
    '''
    from calibre.gui2 import error_dialog, info_dialog

    column = prefs['custom_column']
    if not column:
        error_dialog(
            gui, 'Koreader MD5',
            'No custom column configured. Please configure the plugin first '
            '(Preferences → Plugins → Koreader MD5 → Customize).',
            show=True
        )
        return

    fmt_pref = prefs.get('format_preference', 'epub')

    rows = gui.library_view.selectionModel().selectedRows()
    if not rows:
        error_dialog(gui, 'Koreader MD5', 'No books selected.', show=True)
        return

    ids = list(map(gui.library_view.model().id, rows))
    db = gui.current_db.new_api

    # Verify the column exists
    if column not in db.field_metadata.custom_field_metadata():
        error_dialog(
            gui, 'Koreader MD5',
            f'Custom column "{column}" not found in library. '
            'Please reconfigure the plugin.',
            show=True
        )
        return

    updated = 0
    errors = []

    for book_id in ids:
        formats = db.formats(book_id)
        if not formats:
            continue

        # Pick preferred format, fall back to first available
        fmt = fmt_pref.upper() if fmt_pref.upper() in formats else formats[0]

        # Hash based on configured mode
        hash_mode = prefs.get('hash_mode', 'exported')
        if hash_mode == 'raw':
            # Hash the file as-is from calibre's library
            h = hash_raw(db, book_id, fmt)
        else:
            # Export with metadata applied (matches device copy), then hash
            h = export_and_hash(db, book_id, fmt)

        if h:
            try:
                db.set_field(column, {book_id: h})
                updated += 1
            except Exception as e:
                errors.append(f'Book {book_id}: {e}')
        else:
            errors.append(f'Book {book_id}: could not compute hash')

    msg = f'Updated {updated} of {len(ids)} book(s).'
    if errors:
        msg += f'\n\n{len(errors)} error(s):\n' + '\n'.join(errors[:10])

    info_dialog(gui, 'Koreader MD5', msg, show=True)
