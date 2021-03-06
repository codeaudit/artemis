import pickle
from artemis.fileman.file_getter import get_temp_file, get_file_and_cache
from artemis.fileman.images2gif import readGif
from decorator import contextmanager
import os
from artemis.fileman.local_dir import get_local_path
import numpy as np
import re
from datetime import datetime


def smart_save(obj, relative_path, remove_file_after = False):
    """
    Save an object locally.  How you save it depends on its extension.
    Extensions currently supported:
        pkl: Pickle file.
        That is all.
    :param obj: Object to save
    :param relative_path: Path to save it, relative to "Data" directory.  The following placeholders can be used:
        %T - ISO time
        %R - Current Experiment Record Identifier (includes experiment time and experiment name)
    :param remove_file_after: If you're just running a test, it's good to verify that you can save, but you don't
        actually want to leave a file behind.  If that's the case, set this argument to True.
    """
    if '%T' in relative_path:
        iso_time = datetime.now().isoformat().replace(':', '.').replace('-', '.')
        relative_path = relative_path.replace('%T', iso_time)
    if '%R' in relative_path:
        from artemis.fileman.experiment_record import get_current_experiment_id
        relative_path = relative_path.replace('%R', get_current_experiment_id())
    _, ext = os.path.splitext(relative_path)
    local_path = get_local_path(relative_path, make_local_dir=True)

    print 'Saved object <%s at %s> to file: "%s"' % (obj.__class__.__name__, hex(id(object)), local_path)
    if ext=='.pkl':
        with open(local_path, 'w') as f:
            pickle.dump(obj, f)
    elif ext=='.pdf':
        obj.savefig(local_path)
    else:
        raise Exception("No method exists yet to save '.%s' files.  Add it!" % (ext, ))

    if remove_file_after:
        os.remove(local_path)

    return local_path


def smart_load(location, use_cache = False):
    """
    Load a file, with the method based on the extension.  See smart_save doc for the list of extensions.
    :param location: Identifies file location.
        If it's formatted as a url, it's downloaded.
        If it begins with a "/", it's assumed to be a local path.
        Otherwise, it is assumed to be referenced relative to the data directory.
    :param use_cache: If True, and the location is a url, make a local cache of the file for future use (note: if the
        file at this url changes, the cached file will not).
    :return: An object, whose type depends on the extension.  Generally a numpy array for data or an object for pickles.
    """
    assert isinstance(location, str), 'Location must be a string!  We got: %s' % (location, )
    with smart_file(location, use_cache=use_cache) as local_path:
        ext = os.path.splitext(local_path)[1].lower()
        if ext=='.pkl':
            with open(local_path) as f:
                obj = pickle.load(f)
        elif ext=='.gif':
            frames = readGif(local_path)
            if frames[0].shape[2]==3 and all(f.shape[2] for f in frames[1:]):  # Wierd case:
                obj = np.array([frames[0]]+[f[:, :, :3] for f in frames[1:]])
            else:
                obj = np.array(readGif(local_path))
        elif ext in ('.jpg', '.jpeg', '.png'):
            obj = _load_image(local_path)
        else:
            raise Exception("No method exists yet to load '%s' files.  Add it!" % (ext, ))
    return obj


def smart_load_image(location, max_resolution = None, force_rgb=False, use_cache = False):
    """
    Load an image into a numpy array.

    :param location: Identifies file location.
        If it's formatted as a url, it's downloaded.
        If it begins with a "/", it's assumed to be a local path.
        Otherwise, it is assumed to be referenced relative to the data directory.
    :param max_resolution: Maximum resolution (size_y, size_x) of the image
    :param force_rgb: Force an RGB representation (transform greyscale and RGBA images into RGB)
    :param use_cache: If True, and the location is a url, make a local cache of the file for future use (note: if the
        file at this url changes, the cached file will not).
    :return: An object, whose type depends on the extension.  Generally a numpy array for data or an object for pickles.
    """
    with smart_file(location, use_cache=use_cache) as local_path:
        return _load_image(local_path, max_resolution = max_resolution, force_rgb=force_rgb)


def _load_image(local_path, max_resolution = None, force_rgb = False):
    """
    :param local_path: Local path to the file
    :param max_resolution: Maximum resolution (size_y, size_x) of the image
    :param force_rgb: Force an RGB representation (transform greyscale and RGBA images into RGB)
    :return: The image array, which can be:
        (size_y, size_x, 3) For a colour RGB image
        (size_y, size_x) For a greyscale image
        (size_y, size_x, 4) For an image with transperancy (Note: Disabled for now)
    """
    # TODO: Consider replacing PIL with scipy
    ext = os.path.splitext(local_path)[1].lower()
    assert ext in ('.jpg', '.jpeg', '.png', '.gif')
    from PIL import Image
    pic = Image.open(local_path)

    if max_resolution is not None:
        max_width, max_height = max_resolution
        pic.thumbnail((max_width, max_height), Image.ANTIALIAS)

    pic_arr = np.asarray(pic)

    if force_rgb:
        if pic_arr.ndim==2:
            pic_arr = np.repeat(pic_arr[:, :, None], 3, axis=2)
        elif pic_arr.shape[2]==4:
            pic_arr = pic_arr[:, :, :3]
        else:
            assert pic_arr.shape[2]==3
    return pic_arr


@contextmanager
def smart_file(location, use_cache = False):
    """
    :param location: Specifies where the file is.
        If it's formatted as a url, it's downloaded.
        If it begins with a "/", it's assumed to be a local path.
        Otherwise, it is assumed to be referenced relative to the data directory.
    :param use_cache: If True, and the location is a url, make a local cache of the file for future use (note: if the
        file at this url changes, the cached file will not).
    :yield: The local path to the file.
    """
    its_a_url = is_url(location)
    if its_a_url:
        if use_cache:
            local_path = get_file_and_cache(location)
        else:
            local_path = get_temp_file(location)
    else:
        local_path = get_local_path(location)

    yield local_path

    if its_a_url and not use_cache:
        os.remove(local_path)


def is_url(path):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return True if re.match(regex, path) else False
