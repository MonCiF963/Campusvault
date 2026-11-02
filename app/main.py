from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field
app = FastAPI(title="CampusVault", version="1.0.0")

# ---------- DTOs: what may come in, what may go out ----------

class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    body: str = Field(default="", max_length=5000)


class NoteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=100)
    body: str | None = Field(default=None, max_length=5000)


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime

    # ---------- "Database": a dict in memory ----------

NOTES: dict[int, dict] = {}
_next_id = 1

# ---------- Health check ----------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post(
    "/notes",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED
)
def create_note(data: NoteCreate, response: Response):
    global _next_id

    note = {
        "id": _next_id,
        "title": data.title,
        "body": data.body,
        "created_at": datetime.now(timezone.utc)
    }

    NOTES[_next_id] = note

    response.headers["Location"] = f"/notes/{_next_id}"

    _next_id += 1

    return note

@app.get("/notes", response_model=list[NoteOut])
def get_notes(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    return list(NOTES.values())[offset:offset + limit]

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    note = NOTES.get(note_id)

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note

@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteUpdate):
    note = NOTES.get(note_id)

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    updates = data.model_dump(exclude_unset=True)

    note.update(updates)

    return note

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    del NOTES[note_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)