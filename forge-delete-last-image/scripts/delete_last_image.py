
import os

from modules import script_callbacks, shared
from modules.ui_components import ToolButton


IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp",
    ".bmp", ".tif", ".tiff"
}

galleries = {}


def delete_last_image(tabname):
    output_dir = (
        shared.opts.outdir_samples
        or getattr(shared.opts, f"outdir_{tabname}_samples")
    )

    if not output_dir or not os.path.isdir(output_dir):
        print("[Delete Last Image] Output directory not found.")
        return

    latest_file = None
    latest_time = -1

    for root, dirs, files in os.walk(output_dir):
        for filename in files:
            if os.path.splitext(filename)[1].lower() not in IMAGE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)

            try:
                modified = os.path.getmtime(filepath)
                if modified > latest_time:
                    latest_time = modified
                    latest_file = filepath
            except OSError:
                continue

    if latest_file and os.path.isfile(latest_file):
        try:
            os.remove(latest_file)
            print(f"[Delete Last Image] Deleted: {latest_file}")
        except OSError as e:
            print(f"[Delete Last Image] Error: {e}")
    else:
        print("[Delete Last Image] No generated images found.")


def after_component(component, **kwargs):
    elem_id = kwargs.get("elem_id") or getattr(component, "elem_id", None)

    # Remember the gallery component.
    if elem_id in ("txt2img_gallery", "img2img_gallery"):
        tabname = elem_id.replace("_gallery", "")
        galleries[tabname] = component
        return

    # Add the delete button inside the existing image-buttons row.
    if elem_id not in ("txt2img_open_folder", "img2img_open_folder"):
        return

    tabname = elem_id.replace("_open_folder", "")

    if tabname not in galleries:
        return

    button = ToolButton(
        value="✕",
        elem_id=f"{tabname}_delete_last_image",
        tooltip="Delete latest generated image from disk",
    )

    button.click(
        fn=lambda tab=tabname: delete_last_image(tab),
        inputs=[],
        outputs=[],
        queue=False,
        show_progress=False,
    )


script_callbacks.on_after_component(after_component)
