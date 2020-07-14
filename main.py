import os
import shutil
import uuid
import io
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Response, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, FileResponse
from starlette.requests import Request
from pdf_diff import command_line

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIFF_ID_HEADER = "X-PdfDiff-Id"
DIFF_JSON = "diff.json"
DIFF_PDF = "diff.pdf"
BASE_WORKING_DIR = "working_dir"


@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/diff")
def pdf_diff(response: Response,
             prev: UploadFile = File(...),
             current: UploadFile = File(...),
             img: Optional[bool] = True):
    diff_id = str(uuid.uuid4())
    working_dir = BASE_WORKING_DIR + "/" + diff_id + "/"
    # Create a new directory structure for each request to store the uploaded files and diff.pdf
    os.makedirs(working_dir)
    prev_path = copy_file(working_dir, prev, 'prev.pdf')
    current_path = copy_file(working_dir, current, 'current.pdf')
    changes = command_line.compute_changes(prev_path, current_path)

    json_path = working_dir + "/" + DIFF_JSON
    import json
    with open(json_path, 'w') as fp:
        json.dump(changes, fp)

    if img:
        pdf_path = working_dir + "/" + DIFF_PDF
        render_changes(changes, pdf_path)
        custom_headers = {
            DIFF_ID_HEADER: diff_id,
            'access-control-expose-headers': DIFF_ID_HEADER
        }
        return FileResponse(pdf_path,
                            media_type="application/pdf",
                            headers=custom_headers,
                            filename='diff.pdf')
    else:
        response.headers['access-control-expose-headers'] = DIFF_ID_HEADER
        response.headers[DIFF_ID_HEADER] = diff_id
        return changes


@app.get("/diff/{diff_id}")
def get_diff_by_id(response: Response,
                   diff_id: str = Path(..., title="Diff Id to return"),
                   img: Optional[bool] = True):
    working_dir = BASE_WORKING_DIR + "/" + diff_id

    json_path = working_dir + "/" + DIFF_JSON
    json_exists = os.path.exists(json_path)

    pdf_path = working_dir + "/" + DIFF_PDF
    pdf_exists = os.path.exists(pdf_path)
    if (not json_exists and not pdf_exists):
        raise HTTPException(
            status_code=404,
            detail="Diff Id not found. Consider creating a new Diff Id.")

    # If only JSON exists, generate the PDF and return it, else return PDF directly
    if json_exists and not pdf_exists:
        import json
        with open(json_path, 'r') as json_file:
            changes = json.load(json_file)
        render_changes(changes, pdf_path, optimize=True)

    if img:
        return FileResponse(pdf_path,
                            media_type="application/pdf",
                            filename='diff.pdf')
    else:
        import json
        with open(json_path, 'r') as json_file:
            changes = json.load(json_file)
        return changes


def copy_file(upload_directory: str, source: UploadFile, filename: str):
    final_file = os.path.join(upload_directory, filename)
    file_to_copy_to = open(final_file, 'wb+')
    shutil.copyfileobj(source.file, file_to_copy_to)
    file_to_copy_to.close()
    return final_file


def render_changes(changes, pdf_path, optimize=False):
    img = command_line.render_changes(changes, "strike,box".split(','), 900)
    rgb_img = img.convert('RGB')
    rgb_img.save(
        pdf_path,
        "pdf",
        save_all=True,
        title='Textual Differences',
        producer='PDF-Diff/v0.1'
    )
