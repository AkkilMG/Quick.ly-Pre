# (c) 2022-2023, Akkil M G (https://github.com/HeimanPictures)
# License: GNU General Public License v3.0


import random
import string
import requests
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from config import *

router = APIRouter()

templates = Jinja2Templates(directory=["templates", "templates/app", "templates/page"])


# Home
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context={
        "request": request,
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("home.html", context)

@router.post("/", response_class=HTMLResponse)
async def home(request: Request):
    form_data = await request.form()
    url = form_data.get("url")
    short = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    while await mongodb.find_one({"short": short}):
        short = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    await mongodb.insert_one({
        "url": url,
        "short": short,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "type": 0,
        "views": 0,
        "ads": 0,
        "report": 0,
    })
    context={
        "request": request,
        "short": f"{DOMAIN}/s/{short}",
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("home.html", context)

# Secured Form
@router.get("/secured", response_class=HTMLResponse)
async def securedShortHome(request: Request):
    context={
        "request": request,
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("securedShortForm.html", context)

@router.post("/secured", response_class=HTMLResponse)
async def securedShortHome(request: Request):
    form_data = await request.form()
    url = form_data.get("url")
    password = form_data.get("password")
    scode = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    while await mongodb.find_one({"scode": scode}):
        scode = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    await mongodb.insert_one({
        "url": url,
        "scode": scode,
        "password": password,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "type": 1,
        "views": 0,
        "ads": 0
    })
    context={
        "request": request,
        "scode": f"{DOMAIN}secured/{scode}",
        "password": password,
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("securedShortForm.html", context)

# Short Redirect
@router.get("/s/{short}")
async def short(short: str):
    rs = await mongodb.find_one({"short": short})
    if rs:
        await mongodb.update_one({"short": short}, { '$inc': { 'views': 1 } })
        return RedirectResponse(url=rs["url"], status_code=301)
    else:
        return RedirectResponse(url=f"/error", status_code=301)

# Delete shorten
@router.get("/delete/{password}")
async def deleteShorten(request: Request, id: str, password: str):
    if password == PASS:
        context={
            "request": request,
            "bg": request.url_for("static", path="home.jpg")
        }
        return templates.TemplateResponse("delete.html", context)
    else:
        return RedirectResponse(url=f"/error", status_code=301)

@router.post("/delete/{password}")
async def deleteShorten(request: Request, password: str):
    if password == PASS:
        try:
            form_data = await request.form()
            try:
                await mongodb.delete_one({"short": form_data.get("short")})
            except:
                try:
                    await mongodb.delete_one({"scode": form_data.get("short")})
                except:
                    context={
                        "request": request,
                        "bg": request.url_for("static", path="home.jpg"),
                        "password": password,
                        "message": "Deleted Successfully"
                    }
                    return templates.TemplateResponse("delete.html", context)
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "password": password,
                "message": "Deleted Successfully"
                }
        except Exception as e:
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "error": f"Error sending message: {e}"
            }
    else:
        context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "error": f"Error sending message: Some issue"
            }
    return templates.TemplateResponse("delete.html", context)
    
# Secured Short Redirect
@router.get("/secured/{scode}")
async def securedShort(request: Request, scode: str):
    rs = await mongodb.find_one({"scode": scode})
    if rs['type'] == 1:
        context={
            "request": request,
            "bg": request.url_for("static", path="home.jpg"),
            "scode": scode
        }
        return templates.TemplateResponse("securedShort.html", context)
    else:
        return RedirectResponse(url=f"/error", status_code=301)
    
@router.post("/secured/{scode}")
async def securedShort(request: Request, scode: str):
    rs = await mongodb.find_one({"scode": scode})
    if rs['type'] == 1:
        form_data = await request.form()
        password = form_data.get("password")
        res = await mongodb.find_one({"scode": scode, "password": password})
        if res:
            await mongodb.update_one({"scode": scode}, {"$inc": {"views": 1}})
            return RedirectResponse(url=rs["url"], status_code=301)
        else:
            return RedirectResponse(url=f"/error", status_code=301)
    else:
        return RedirectResponse(url=f"/error", status_code=301)

# Report
@router.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    context={
        "request": request,
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("report.html", context)

@router.post("/report", response_class=HTMLResponse)
async def report(request: Request):
    form_data = await request.form()
    try:
        payload = {
            "chat_id": CHAT_ID, 
            "text": f"#report\n\nNew message from Shortner:\n\nURL: {form_data.get('url')}\nMessage: {form_data.get('message')}"
        }
        res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", headers={"Content-Type": "application/json"}, json=payload)
        if res.status_code == 200:
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "message": "Reported the url successfully!"
            }
        else:
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "error": f"Error sending message: {res.status_code} {res.text}"
            }
        return templates.TemplateResponse("report.html", context)
    except Exception as e:
        print(e)
        return RedirectResponse(f"{DOMAIN}/error")
    
# Contact
@router.post("/contact", response_class=HTMLResponse)
async def contact(request: Request, response: Response):
    try:
        form_data = await request.form()
        payload = {
            "chat_id": CHAT_ID, 
            "text": f"#contact\n\nNew message from Shortner:\n\nEmail: " + form_data.get("email") + "\nSubject: " + form_data.get("subject") + "\nMessage: " + form_data.get("message")
        }
        res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", headers={"Content-Type": "application/json"}, json=payload)
        if res.status_code == 200:
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "message": "Message sent successfully!"
            }
        else:
            context={
                "request": request,
                "bg": request.url_for("static", path="home.jpg"),
                "message": f"Error sending message: {res.status_code} {res.text}"
            }
        return templates.TemplateResponse("contact.html", context)
    except Exception as e:
        print(e)
        return RedirectResponse(f"{DOMAIN}/error")

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, response: Response):
    context={
        "request": request,
        "bg": request.url_for("static", path="home.jpg")
    }
    return templates.TemplateResponse("contact.html", context)
