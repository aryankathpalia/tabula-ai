import os
import uuid
import requests


def upload_file(file):

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"

    url = f"{SUPABASE_URL}/storage/v1/object/documents/{filename}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": file.content_type
    }


    file.file.seek(0)

    response = requests.post(
        url,
        headers=headers,
        data=file.file.read()
    )

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/documents/{filename}"

    return public_url