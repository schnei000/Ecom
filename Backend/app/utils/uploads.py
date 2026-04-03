import os
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..validators import ValidationError

TRUTHY_VALUES = {"1", "true", "yes", "on"}


def parse_bool(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in TRUTHY_VALUES


def _get_file_extension(filename):
    return Path(filename).suffix.lower().lstrip(".")


def validate_product_image(image_file: FileStorage):
    if image_file is None or not image_file.filename:
        raise ValidationError("Aucun fichier image fourni.")

    filename = secure_filename(image_file.filename)
    if not filename:
        raise ValidationError("Nom de fichier image invalide.")

    extension = _get_file_extension(filename)
    allowed_extensions = current_app.config.get("PRODUCT_IMAGE_ALLOWED_EXTENSIONS", set())
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValidationError(f"Format image non supporté. Formats autorisés: {allowed}.")

    mimetype = (image_file.mimetype or "").lower()
    allowed_mimetypes = current_app.config.get("PRODUCT_IMAGE_ALLOWED_MIMETYPES", set())
    if mimetype and mimetype not in allowed_mimetypes:
        raise ValidationError("Type MIME image non supporté.")

    max_bytes = int(current_app.config.get("PRODUCT_IMAGE_MAX_BYTES", 5 * 1024 * 1024))
    stream = image_file.stream
    current_position = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(current_position)

    if size <= 0:
        raise ValidationError("Le fichier image est vide.")
    if size > max_bytes:
        raise ValidationError(f"L'image dépasse la taille maximale autorisée ({max_bytes // (1024 * 1024)} MB).")

    return filename, extension


def delete_product_image(filename):
    if not filename:
        return

    upload_dir = Path(current_app.config["PRODUCT_IMAGE_UPLOAD_FOLDER"])
    target = upload_dir / filename
    try:
        target.unlink(missing_ok=True)
    except OSError:
        current_app.logger.warning("Unable to delete product image %s", target)


def save_product_image(image_file: FileStorage):
    _, extension = validate_product_image(image_file)

    upload_dir = Path(current_app.config["PRODUCT_IMAGE_UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    image_file.save(destination)

    return filename
