"""
app/main.py

Main FastAPI entrypoint with both API routes and server-rendered pages.
"""

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session

from app import models, crud, scheduler, auth
from app.config import DATABASE_URL
from fastapi import Form 

# --- App & DB setup ---
engine = create_engine(DATABASE_URL, echo=False)
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Prospects API & HTMX endpoints ---

@app.post("/prospects/")
def create_prospect(
    name: str = Form(...),
    email: str = Form(...),
    language: str = Form(...),
    title: str = Form(""),
    session: Session = Depends(get_session),
    user=Depends(auth.get_current_user),
):
    data = models.Prospect(name=name, email=email, language=language, title=title, user_id=user.id)
    prospect = crud.create_prospect(session, data)
    scheduler.schedule_sequence_for_prospect(session, prospect, user.id)
    
    # Return the updated HTML fragment
    prospects = crud.get_prospects(session, user.id)
    return templates.TemplateResponse("_prospect_list.html", {
        "request": Request(scope={}),  # Temporary fix if needed
        "prospects": prospects
    })

    # HTMX form client
    form = await request.form()
    prospect = models.Prospect(
        user_id=user.id,
        title=form.get("title"),
        name=form["name"],
        email=form["email"],
        language=form["language"],
        type_id=None,
    )
    prospect = crud.create_prospect(session, prospect)
    scheduler.schedule_sequence_for_prospect(session, prospect, user.id)

    prospects = crud.get_prospects(session, user.id)
    return templates.TemplateResponse(
        "_prospect_list.html",
        {"request": request, "prospects": prospects},
    )

@app.delete("/prospects/{prospect_id}", response_class=HTMLResponse)
async def delete_prospect(
    prospect_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user=Depends(auth.get_current_user),
):
    success = crud.delete_prospect(session, prospect_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    prospects = crud.get_prospects(session, user.id)
    return templates.TemplateResponse(
        "_prospect_list.html",
        {"request": request, "prospects": prospects},
    )

@app.get("/prospects-page", response_class=HTMLResponse)
def prospects_page(
    request: Request,
    session: Session = Depends(get_session),
    user=Depends(auth.get_current_user),
):
    prospects = crud.get_prospects(session, user.id)
    return templates.TemplateResponse(
        "prospects.html",
        {"request": request, "prospects": prospects, "user": user},
    )
from fastapi import Form

@app.post("/prospects/", response_class=HTMLResponse)
def create_prospect_form(
    name: str = Form(...),
    email: str = Form(...),
    session: Session = Depends(get_session),
    user=Depends(auth.get_current_user)
):
    new_prospect = models.Prospect(name=name, email=email, user_id=user.id)
    session.add(new_prospect)
    session.commit()
    session.refresh(new_prospect)
    scheduler.schedule_sequence_for_prospect(session, new_prospect, user.id)
    return templates.TemplateResponse("_prospect_list.html", {
        "request": Request,
        "prospects": crud.get_prospects(session, user.id),
        "user": user
    })


@app.delete("/prospects/{prospect_id}", response_class=HTMLResponse)
def delete_prospect(prospect_id: int, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    crud.delete_prospect(session, prospect_id, user.id)
    return templates.TemplateResponse("_prospect_list.html", {
        "request": Request,
        "prospects": crud.get_prospects(session, user.id),
        "user": user
    })

@app.get("/prospects/partial", response_class=HTMLResponse)
def get_prospect_list_partial(request: Request, session: Session = Depends(get_session), user=Depends(auth.get_current_user)):
    prospects = crud.get_prospects(session, user.id)
    return templates.TemplateResponse("_prospect_list.html", {
        "request": request,
        "prospects": prospects,
        "user": user
    })
