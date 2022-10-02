import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from numpy import datetime_data
import requests
import json
from urllib.request import urlopen

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

with urlopen("http://maqe.github.io/json/authors.json") as url:
    users = json.loads(url.read().decode())
    # print(users)

with urlopen("http://maqe.github.io/json/posts.json") as url:
    posts = json.loads(url.read().decode())
    # print(posts)


@app.get("/")
async def read_item(request: Request):
    import datetime
    import urllib
    posts_ext = []
    print("request: ", request.client.host)

    response = requests.get(
        f'http://api.hostip.info/get_html.php?ip={request.client.host}&position=true')

    # response_json = json.loads(response.content.decode().replace("\n", ","))
    response_str = response.content.decode().replace(": ", ",").replace("\n", ",")
    response_dict = response_str.split(",")
    print(response_dict)

    timezone = get_timezone(response_dict[3])
    # timezone = get_timezone("Bangkok")

    # tz = datetime.timedelta(seconds=int(request.cookies["timezone"]))
    # print("tz :", tz)
    color_switch = False
    for post in posts:
        post_ext = post
        post_ext["switch"] = color_switch
        created_at = post_ext["created_at"].replace(
            "T", " ").replace("Z", "")
        post_ext["created_at"] = format_datetime(created_at)
        post_ext["author"] = next(
            (user for user in users if user.get("id") == post.get("author_id")), None)
        posts_ext.append(post_ext)
        color_switch = not color_switch
    data = {"timezone": timezone, "posts": posts_ext}
    return templates.TemplateResponse("listview.html", {"request": request, "data": data})


@app.get("/a")
async def getdataList():
    return users


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


def get_timezone(city_name):
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder

    geolocator = Nominatim(user_agent="MAQE")
    location = geolocator.geocode(city_name)
    if location:
        print(f"location - {location.latitude}, {location.longitude}")
        tz_finder_inst = TimezoneFinder()
        timezone_is = tz_finder_inst.timezone_at(
            lng=location.longitude, lat=location.latitude)
        print(f"timezone at - {timezone_is}")
        return timezone_is
    else:
        print("Not found (Default: Asia/Bangkok)")
        return "Not found (Default: Asia/Bangkok)"


def format_datetime(dt):
    from datetime import datetime
    print(dt)
    date_time_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    DoW = date_time_obj.strftime('%A')
    MonthN = date_time_obj.strftime('%B')
    DateD = date_time_obj.day
    DateY = date_time_obj.year
    TimeH = date_time_obj.hour
    TimeM = date_time_obj.minute

    return f"{DoW}, {MonthN} {DateD}, {DateY}, {TimeH}:{TimeM}"
