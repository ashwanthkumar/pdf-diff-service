import os
import shutil
import uuid
import io
from typing import Optional

from fastapi import FastAPI, File, UploadFile
from starlette.responses import StreamingResponse, FileResponse
from pdf_diff import command_line

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/diff/")
def pdf_diff(prev: UploadFile = File(...),
             current: UploadFile = File(...),
             img: Optional[bool] = True):
    working_dir = "working_dir/" + str(uuid.uuid4()) + "/"
    # Create a new directory structure for each request to store the uploaded files and diff.png
    os.makedirs(working_dir)
    prev_path = copy_file(working_dir, prev)
    current_path = copy_file(working_dir, current)
    changes = command_line.compute_changes(prev_path, current_path)
    if img:
        diff_png_path = working_dir + "/diff.png"
        img = command_line.render_changes(changes, "strike,box".split(','), 900)
        img.save(diff_png_path, "png")
        img.seek(0)
        return FileResponse(diff_png_path, media_type="image/png")
    else:
        return changes


def copy_file(upload_directory: str, source: UploadFile):
    final_file = os.path.join(upload_directory, source.filename)
    file_to_copy_to = open(final_file, 'wb+')
    shutil.copyfileobj(source.file, file_to_copy_to)
    file_to_copy_to.close()
    return final_file
