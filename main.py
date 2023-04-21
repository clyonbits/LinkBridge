from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

BACKEND = "http://linkbridge.click/"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Account(BaseModel):
    username: str
    description: str
    links: dict

@app.get("/")
def home():
    with open("frontend/index.html") as index:
        return HTMLResponse(index.read())
    
@app.get("/make-bridge")
def make_bridge():
    with open("frontend/make-bridge.html") as index:
        return HTMLResponse(index.read())

@app.get("/raw/{username}")
def get_account(username: str):
    with open("accounts.json") as accounts_file:
        accounts = json.load(accounts_file)
        for account in accounts:
            if account["username"] == username:
                return account
        raise HTTPException(status_code=404, detail="Account Not Found")

@app.get("/{username}")
def get_account_page(account = Depends(get_account)):
    # Cargar HTML y CSS
    with open("assets/user_template.html", "r") as template:
        page = template.read().replace("username-visible", account["username"]).replace("description-visible", account["description"])
        soup = BeautifulSoup(page, 'html.parser')
        links_div = soup.find('div', {'class': 'links'})
        for website, url in account["links"].items():
            links_div.append(soup.new_tag("br"))
            btn = soup.new_tag('a', target="_blank")
            if "http://" in url or "https://" in url:
                btn["href"] = url
            else:
                btn["href"] = f"http://{url}"
            btn["class"] = "button"
            btn.string = website
            links_div.append(btn)
            links_div.append(soup.new_tag("br"))
        page = soup.prettify()
        return HTMLResponse(page)
            
@app.post("/")
def post_account_page(account: Account):
    with open("accounts.json", "r") as accounts_file:
        accounts = json.load(accounts_file)
    new_accounts = {
        "username": account.username,
        "description": account.description,
        "links": account.links
    }
    accounts.append(new_accounts)
    with open('accounts.json', 'w') as accounts_file:
        json.dump(accounts, accounts_file)
    return f"{BACKEND}{account.username}"