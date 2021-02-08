import os
from pathlib import Path
from .random_string import get_random_string
from django.conf import settings

def store_gContent(username, obj, location=settings.MEDIA_ROOT):
    obj.save()
    init_path = obj.content.path
    name = obj.content.name
    ext = name.split('.')[-1]
    cType, obj = get_content_type(ext, obj)
    path = Path(f"{location}{cType}/{username}/")
    path.mkdir(parents=True, exist_ok=True)
    new_path = f"{path}/{get_random_string()}.{ext}"
    os.rename(init_path, new_path)
    return obj

def get_content_type(ext, obj):
    image_exts = ['jpg', 'jpeg', 'jpe', 'jif', 'jfif', 'jfi', 'png', 'gif', 'webp', 'tiff', 'tif', 'psd',
        'bmp', 'dib', 'heif', 'heic', 'ind', 'indd', 'indt', 'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2', 'svg',
        'svgz', 'ai', 'eps']
    video_exts = ['webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'ogg', 'mp4', 'm4p', 'm4v', 'avi', 'wmv', 'mov',
    'qt', 'flv', 'swf', 'avchd']
    if ext.lower() in image_exts:
        direc = 'image'
        if hasattr(obj, 'content_type'):
            obj.content_type = 0
    elif ext.lower() in video_exts:
        direc = 'video'
        if hasattr(obj, 'content_type'):
            obj.content_type = 1
    else:
        direc = 'script'
        if hasattr(obj, 'content_type'):
            obj.content_type = 2
    return direc, obj