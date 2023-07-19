#  by ReYeS
#    _;)  ~~8:> ~~8:>
#  Update by V¡ktor
#  https://github.com/ViktorSky/amino-coin-generator

import os
import time
import json
from datetime import datetime
from random import randint
from threading import Thread
from base64 import b64encode
from hashlib import sha1
from hmac import new

os.system('pip install -r requirements.txt')

from websocket import WebSocketApp, WebSocketConnectionClosedException
from requests import Session
from yarl import URL
import pytz
from flask import Flask
from json_minify import json_minify


parameters = {
    "community-link":
        "http://aminoapps.com/c/RogerioCena",
    "accounts-file":
        "./acc.json",
    "proxies": { 
        "http": None
    }
}

""""proxies": { 
        "http": "socks5://holayo23:Nogayss123@185.199.229.156:7492", 
        "https": "socks5://holayo23:Nogayss123@185.199.229.156:7492"
    }"""
  
PREFIX = '19'
DEVKEY = 'e7309ecc0953c6fa60005b2765f99dbbc965c8e9'
SIGKEY = 'dfa5ed192dda6e88a12fe12130dc6206b1251e44'

# -----------------FLASK-APP-----------------
flask_app = Flask('amino-coin-generator')
@flask_app.route('/')
def home():
    return "~~8;> ~~8;>"

def run():
    flask_app.run('0.0.0.0', randint(2000, 9000))
# -------------------------------------------


class Client:
    api = "https://service.aminoapps.com/api/v1"

    def __init__(self, device=None, proxies=None) -> None:
        self.device = device or self.generate_device()
        self.proxies = proxies or {}
        self.session = Session()
        self.socket = None
        self.socket_thread = None
        self.sid = None
        self.auid = None

    def build_headers(self, data=None):
        headers = {
            "NDCDEVICEID": self.device,
            "SMDEVICEID": "b89d9a00-f78e-46a3-bd54-6507d68b343c",
            "Accept-Language": "en-EN",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "Apple iPhone12,1 iOS v15.5 Main/3.12.2",
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        if data:
            headers["NDC-MSG-SIG"] = self.generate_signature(data)
        if self.sid:
            headers["NDCAUTH"] = "sid=%s" % self.sid
        if self.auid:
            headers["AUID"] = self.auid
        return headers

    def generate_signature(self, data):
        return b64encode(
            bytes.fromhex(PREFIX) + new(
                bytes.fromhex(SIGKEY),
                data.encode("utf-8"),
                sha1
            ).digest()
        ).decode("utf-8")

    def generate_device(self):
        info = bytes.fromhex(PREFIX) + os.urandom(20)
        return info.hex() + new(
            bytes.fromhex(DEVKEY),
            info, sha1
        ).hexdigest()

    def ws_send(self, data):
        if self.sid is None:
            return
        final = f"%s|%d" % (self.device, int(time.time() * 1000))
        kwargs = {}
        proxy = self.proxies.get('https')
        if proxy:
            url = URL(f"https://{proxy}" if "http" not in proxy else proxy)
            kwargs["proxy_type"] = url.scheme if 'http' in url.scheme else 'https'
            kwargs["http_proxy_host"] = url.host
            kwargs["http_proxy_port"] = url.port
            if url.user:
                kwargs["http_proxy_auth"] = (url.user, url.password)
        socket_url = URL("wss://ws%d.aminoapps.com/?signbody=%s")
        if not kwargs.get("proxy_type", "https").endswith("s"):
            socket_url = socket_url.with_scheme("ws")
        for n in range(4, 0, -1):
            try:
                self.socket = WebSocketApp(
                    socket_url.human_repr() % (n, final.replace('|', '%7C')),
                    header=self.build_headers(final)
                )
                self.socket_thread = Thread(
                    target=self.socket.run_forever,
                    kwargs=kwargs
                )
                self.socket_thread.start()
                time.sleep(3.2)
                return self.socket.send(data)
            except WebSocketConnectionClosedException:
                continue

    def login(self, email, password):
        data = json.dumps({
             "email": email,
             "secret": "0 %s" % password,
             "deviceID": self.device,
             "clientType": 100,
             "action": "normal",
             "timestamp": int(time.time() * 1000)
        })
        request = self.session.post(
            url="%s/g/s/auth/login" % self.api,
            data=data,
            headers=self.build_headers(data),
            proxies=self.proxies
        ).json()
        self.sid = request.get("sid")
        self.auid = request.get("auid")
        return request

    def join_community(self, ndcId, invitationId=None):
        data = {"timestamp": int(time.time() * 1000)}
        if invitationId:
            data["invitationId"] = invitationId
        data = json.dumps(data)
        return self.session.post(
            url="%s/x%s/s/community/join?sid=%s&auid=%s" % (self.api, ndcId, self.sid, self.auid),
            data=data,
            headers=self.build_headers(data),
            proxies=self.proxies
        ).json()

    def send_active_object(self, ndcId, timers=None, timezone=0):
        data = json_minify(json.dumps({
            "userActiveTimeChunkList": timers,
            "timestamp": int(time.time() * 1000),
            "optInAdsFlags": 2147483647,
            "timezone": timezone
        }))
        return self.session.post(
            url="%s/x%s/s/community/stats/user-active-time?sid=%s&auid=%s" % (self.api, ndcId, self.sid, self.auid),
            data=data,
            headers=self.build_headers(data),
            proxies=self.proxies
        ).json()

    def watch_ad(self):
        return self.session.post(
            "%s/g/s/wallet/ads/video/start?sid=%s&auid=%s" % (self.api, self.sid, self.auid),
            headers=self.build_headers(),
            proxies=self.proxies
        ).json()

    
    def get_from_link(self, link):
        print("oi")
        return self.session.get(
            url="%s/g/s/link-resolution?q=%s" % (self.api, link),
            headers=self.build_headers(),
            proxies=self.proxies
        ).json()

    def lottery(self, ndcId, timezone=0):
        data = json.dumps({
            "timezone": timezone,
            "timestamp": int(time.time() * 1000)
        })
        return self.session.post(
            url="%s/x%s/s/check-in/lottery?sid=%s&auid=%s" % (self.api, ndcId, self.sid, self.auid),
            data=data,
            headers=self.build_headers(data),
            proxies=self.proxies
        ).json()

    def show_online(self, ndcId):
        self.ws_send(json.dumps({
            "o": {
                "actions": ["Browsing"],
                "target": "ndc://x%s/" % ndcId,
                "ndcId": int(ndcId),
                "id": "82333"
            },
            "t": 304
        }))


class Config:
    def __init__(self):
        self.account_list = [
        {
            "email": "sshell-3ml82dpri5d8@1secmail.com",
            "password": "rogerio123",
            "device": "19AEFFA8F4E7EC63FD069349456268D6B786B9C4C7B8B031C42E872679E0B29D75B842A66AFAC3CE66",
            "uid": "69928bbf-7ad1-4632-be3e-73d66d3387a3",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI2OTkyOGJiZi03YWQxLTQ2MzItYmUzZS03M2Q2NmQzMzg3YTMiLCAiNSI6IDE2ODgwODU0MzQsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9DFt20eVjhyrvBn1qV63Mn5SkOF4"
        },
        {
            "email": "sshell-4dpymy0j@wuuvo.com",
            "password": "rogerio123",
            "device": "19FE9A0A1E9C44EB66304EF9133424CC0FA69FF7A7173F391FD1AEF516F9721D5AE5E5E63B64AE9C3B",
            "uid": "2d07bcac-89e6-4a50-8eb2-940e0f6188e2",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIyZDA3YmNhYy04OWU2LTRhNTAtOGViMi05NDBlMGY2MTg4ZTIiLCAiNSI6IDE2ODgwNTIzNTMsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB98gaGeHLY1ACscMPLge9f6SEzCa4"
        },
        {
            "email": "sshell-jqau4ovhakf@1secmail.org",
            "password": "rogerio123",
            "device": "1994020B22D8B236E0D199F73E380FB7BDF97A5A79F0239A721D291BC320F33C2D1DCE0110E1C47A2E",
            "uid": "116c7a14-93be-49d8-96db-53ba7afecd55",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIxMTZjN2ExNC05M2JlLTQ5ZDgtOTZkYi01M2JhN2FmZWNkNTUiLCAiNSI6IDE2ODgwNTIzNjAsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9iKvefh3aY9L8Ea2w9qK8m47CITc"
        },
        {
            "email": "sshell-baptb6wvq02@qiott.com",
            "password": "rogerio123",
            "device": "194424D87B5A12D9C00366F5C66C8F403B82BDB9675CAA0461BC470DF6659BFBAF51B5B2B0051BD531",
            "uid": "479e6df5-5d93-49ce-85b8-13fab8891617",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI0NzllNmRmNS01ZDkzLTQ5Y2UtODViOC0xM2ZhYjg4OTE2MTciLCAiNSI6IDE2ODgwNTIzNjYsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9AS9IBRBdw6eUl4KnGd-I7YHHDTE"
        },
        {
            "email": "sshell-w6ekub9tg@qiott.com",
            "password": "rogerio123",
            "device": "19CA99A0BBDBD43B3AE46C6A2508EC2B6E0E9202859A5A03F96630437B50BE4395CF71A5AD8D72AD51",
            "uid": "c1333155-9fa7-49c6-bd6a-c20e7cfdfccf",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJjMTMzMzE1NS05ZmE3LTQ5YzYtYmQ2YS1jMjBlN2NmZGZjY2YiLCAiNSI6IDE2ODgwNTIzNzIsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9qB6xc_fhgq-Fd5OSdPppx5TCIdc"
        },
        {
            "email": "larhonda5866@uorak.com",
            "password": "rogerio123",
            "device": "197A4DA052906DC31BAE9498205AA78F711E0AA6BBF006E640C4E40A475D6D30918A46AE35F02DE9DD",
            "uid": "3225ee04-a987-4320-8b41-3a26cc890f3a",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIzMjI1ZWUwNC1hOTg3LTQzMjAtOGI0MS0zYTI2Y2M4OTBmM2EiLCAiNSI6IDE2ODc4MTg1NzksICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9dKDZUFcmDdC_qc_wfI8ak64c9eE"
        },
        {
            "email": "fatimetu9794@uorak.com",
            "password": "rogerio123",
            "device": "196799C31D861905FEB329C758B27267E67AE4489F8B4CF41046616CCB8723A7A3FDD6D40817494825",
            "uid": "e8364cd0-83c9-409e-a0af-cea16075d936",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJlODM2NGNkMC04M2M5LTQwOWUtYTBhZi1jZWExNjA3NWQ5MzYiLCAiNSI6IDE2ODc4MTg1ODYsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9CRL1yXPbzbLQfXlxaARS-X4EkOE"
        },
        {
            "email": "leidys1561@uorak.com",
            "password": "rogerio123",
            "device": "196335BF8D78205294167556BAD87FC7380D438F3C1EA7C8EF67F695C72C1C393B18E50C9DEDFAC90A",
            "uid": "1eba04ab-ad90-4cc0-aa22-65df3b26ed97",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIxZWJhMDRhYi1hZDkwLTRjYzAtYWEyMi02NWRmM2IyNmVkOTciLCAiNSI6IDE2ODc4MTg1OTQsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9WRm8sgmPdwlhHzwsZO493k6Wp5g"
        },
        {
            "email": "isaiah3854@uorak.com",
            "password": "rogerio123",
            "device": "19CEF1AC30AEBD2815353DFE0A10C0EB7FF7B107AC00853A16E9674F8219BBD1802AFF90B76E682EC2",
            "uid": "d64fda18-80b6-4728-bbe6-2cf37b70f824",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJkNjRmZGExOC04MGI2LTQ3MjgtYmJlNi0yY2YzN2I3MGY4MjQiLCAiNSI6IDE2ODc3MTgxMzIsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9Y3vCmXXWp-LWaS70W4MDzOiEfgw"
        },
        {
            "email": "meirong1653@uorak.com",
            "password": "rogerio123",
            "device": "19F1A005CC9CEA2EAF09B4006D72115A3C3834E303456561CD1572CE4A6C3F512A57FFEC6410C163C0",
            "uid": "077ec313-2686-4c3d-b975-57b7d87f54f8",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIwNzdlYzMxMy0yNjg2LTRjM2QtYjk3NS01N2I3ZDg3ZjU0ZjgiLCAiNSI6IDE2ODc3MTgxNTMsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9oBQBHctj8n_9Q1908Q4l7OyUwvc"
        },
        {
            "email": "sshell-ud47acurg@wuuvo.com",
            "password": "rogerio123",
            "device": "19207792B48316C4336B100118F39C1F77CB3C4D84C2B29CC125CDB6FD781C3A909063A94738BADAD7",
            "uid": "436dc01b-e4d6-4651-a203-50a4d9ee839e",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI0MzZkYzAxYi1lNGQ2LTQ2NTEtYTIwMy01MGE0ZDllZTgzOWUiLCAiNSI6IDE2ODgyMjI2NzMsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB94PfNQ6wNGacjQkjIxwKakQCCDMw"
        },
        {
            "email": "sshell-giy20jcc5s4@kzccv.com",
            "password": "rogerio123",
            "device": "19D6E4FAE31292991B62E17E8CBAE9B1BFEBF37225237EAA2B4968DA7D3837BD754765AD9500149B34",
            "uid": "39b43667-e8bf-4592-ae62-935d372fd36c",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIzOWI0MzY2Ny1lOGJmLTQ1OTItYWU2Mi05MzVkMzcyZmQzNmMiLCAiNSI6IDE2ODg3NjY0OTUsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9VCXj8t144lUWfrqoP8cDrH00xm0"
        },
        {
            "email": "sshell-pq56xyer@1secmail.com",
            "password": "rogerio123",
            "device": "1931D15639D0953DF28E1508D3AC3DD44105A61875E35B59CF4E13DD6455B9850D82B8D36141EACDA6",
            "uid": "ebb2f4d8-d88e-4bf9-bbec-905dc7010056",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJlYmIyZjRkOC1kODhlLTRiZjktYmJlYy05MDVkYzcwMTAwNTYiLCAiNSI6IDE2ODg3NjY1NDMsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9POpPNL3E960s0NqwJxBaSPwsiM4"
        },
        {
            "email": "sshell-kdojlvkc@wuuvo.com",
            "password": "rogerio123",
            "device": "197117D246E56F46C58CDEE636322C4A6049F5DA950E5A29A5A55D90D45746B3A3B9E4F7123041E0A1",
            "uid": "59508dd4-f3b0-4546-92a4-8488ca0d0302",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI1OTUwOGRkNC1mM2IwLTQ1NDYtOTJhNC04NDg4Y2EwZDAzMDIiLCAiNSI6IDE2ODkzMDE4NjEsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9ITq8qyKFtLh9-L0kicba7SvxZ28"
        },
        {
            "email": "sshell-se02fha6@kzccv.com",
            "password": "rogerio123",
            "device": "19C9A978C79628ABF06B1DFCC574926623AA85087957029142430AC6011CA9449F5F61287A9C6C325C",
            "uid": "43be7fb8-6f11-4ae6-9be9-51eb491e49e1",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI0M2JlN2ZiOC02ZjExLTRhZTYtOWJlOS01MWViNDkxZTQ5ZTEiLCAiNSI6IDE2ODkzMDE4NzIsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9ByFV5D7LvyX_Pp9gB0AUwA3lk0c"
        },
        {
            "email": "sshell-nd2ugp6nio@1secmail.net",
            "password": "rogerio123",
            "device": "199C6F2B513CD5DFBF4BC92C71F544021D6E785E8D4B972A351D3AA43092B4579A0D6863750C5C6E1F",
            "uid": "01679373-7a99-4676-b899-82a45b467b6c",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIwMTY3OTM3My03YTk5LTQ2NzYtYjg5OS04MmE0NWI0NjdiNmMiLCAiNSI6IDE2ODkzMDE4NzcsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9PAFc9slt1YxnvuEMs1u3DG-UMZE"
        },
        {
            "email": "sshell-p2g4t710@1secmail.net",
            "password": "rogerio123",
            "device": "193FA184E73F11D53978B068BABFAE8AEF2C6C3968E0319CA5202B254FED1C0064CA652AAF75D0A6D2",
            "uid": "1517de44-06ed-41a5-87c6-ac25ec7b311c",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIxNTE3ZGU0NC0wNmVkLTQxYTUtODdjNi1hYzI1ZWM3YjMxMWMiLCAiNSI6IDE2ODkzNzQ5NzEsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9OgCI73wXZD0zh2EPIiqBM7LOLWo"
        },
        {
            "email": "sshell-our88sfxkib@kzccv.com",
            "password": "rogerio123",
            "device": "191B134C5C88FDB58DDA9879148EADC4CFD7FDBA378F8A1EA70E0AE2B515CF2AB3E7CDED8C39F6B26B",
            "uid": "a1724477-1946-4ff5-ae41-9b5986132094",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJhMTcyNDQ3Ny0xOTQ2LTRmZjUtYWU0MS05YjU5ODYxMzIwOTQiLCAiNSI6IDE2ODk4MDY5NzQsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9NPaS1xuc3ezRmHAweRRvL7g6OPs"
        },
        {
            "email": "sshell-2zq5wo7voumi@wuuvo.com",
            "password": "rogerio123",
            "device": "198AB7CA26C873E8A3AF40CE967C3FE5CAEEA8AFF62D9CB697D5F81311740587EA5511DF1AAE650E9F",
            "uid": "e82318d1-558c-4692-8ad3-e845a9902fa7",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJlODIzMThkMS01NThjLTQ2OTItOGFkMy1lODQ1YTk5MDJmYTciLCAiNSI6IDE2ODk4MDY5OTEsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9fFqXr5Z0NMmEBLfkty2PQ7m9xqo"
        },
        {
            "email": "sshell-lh1a9zoub9@1secmail.org",
            "password": "rogerio123",
            "device": "1951A62E914859847E09D2938DCB42D3B9A37E04D0FE81D856AEBE176B46142739157AA5AB9D93B396",
            "uid": "230f0136-7aaf-42a9-a6e2-1ef069a3de82",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICIyMzBmMDEzNi03YWFmLTQyYTktYTZlMi0xZWYwNjlhM2RlODIiLCAiNSI6IDE2ODk4MDY5OTksICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9DsaDK_dhCoZPWsh96hvXS5yGjc4"
        },
        {
            "email": "sshell-sgop2juw@wuuvo.com",
            "password": "rogerio123",
            "device": "19E803DFA146CA212904340F4855B74BC52C16231BC5521E63F9094A4F7F024A14585B19D8BDFCA1D6",
            "uid": "eb9de665-ef2a-41b2-8acd-5919a6580115",
            "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICJlYjlkZTY2NS1lZjJhLTQxYjItOGFjZC01OTE5YTY1ODAxMTUiLCAiNSI6IDE2ODk4MDcwMDYsICI0IjogIjE3Ny4xMjcuNzguMjQ2IiwgIjYiOiAxMDB9lT6irtL0vuCAZYYVYTCGvGd4N2s"
        }
    ]


class App:
    def __init__(self):
        self.proxies = parameters["proxies"]
        self.client = Client(proxies=self.proxies)
        info = self.client.get_from_link(parameters["community-link"])
        try: extensions = info["linkInfoV2"]["extensions"]
        except KeyError:
            raise RuntimeError('community: %s' % info["api:message"])
        self.ndcId = extensions["community"]["ndcId"]
        self.invitationId = extensions.get("invitationId")

    def tzc(self):
        for _ in ['Etc/GMT' + (f'+{i}' if i > 0 else str(i)) for i in range(-12, 12)]:
            zone = datetime.now(pytz.timezone(_))
            if zone.hour != 23:
                continue
            return int(zone.strftime('%Z').replace('GMT', '00')) * 60
        return 0

    def generation(self, email, password, device, index):
        if device:
            self.client.device = device
        start = time.time()
        try:
            print("Tenta login")
            print(email, password)
            message = self.client.login(email, password)['api:message']
            
            print("\n[\033[1;31mcoins-generator\033[0m][\033[1;34mlogin\033[0m][%s]: %s." % (email, message))
            message = self.client.join_community(self.ndcId, self.invitationId)['api:message']
            print("[\033[1;31mcoins-generator\033[0m][\033[1;36mjoin-community\033[0m]: %s." % message)
            self.client.show_online(self.ndcId)
            message = self.client.lottery(self.ndcId, self.tzc())['api:message']
            print("[\033[1;31mcoins-generator\033[0m][\033[1;32mlottery\033[0m]: %s" % message)
            message = self.client.watch_ad()['api:message']
            print("[\033[1;31mcoins-generator\033[0m][\033[1;33mwatch-ad\033[0m]: %s." % message)
            for _ in range(24):
                timers = [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)]
                message = self.client.send_active_object(self.ndcId, timers, self.tzc())['api:message']
                print("[\033[1;31mcoins-generator\033[0m][\033[1;35mmain-proccess\033[0m][%s]: %s." % (email, message) + " " + str(index))
                time.sleep(4)
            end = int(time.time() - start)
            total = ("%d minutes" % round(end/60)) if end > 90 else ("%d seconds" % end)
            print("[\033[1;31mcoins-generator\033[0m][\033[1;25;32mend\033[0m]: Finished in %s." % total)
        except Exception as error:
            print("[\033[1;31mC01?-G3?3R4?0R\033[0m]][\033[1;31merror\033[0m]]: %s(%s)" % (type(error).__name__, error))
        
        
    def run(self):
        print("\033[1;31m @@@@@@   @@@@@@@@@@   @@@  @@@  @@@   @@@@@@ \033[0m     \033[1;32m @@@@@@@   @@@@@@   @@@  @@@  @@@   @@@@@@\033[0m\n\033[1;31m@@@@@@@@  @@@@@@@@@@@  @@@  @@@@ @@@  @@@@@@@@\033[0m     \033[1;32m@@@@@@@@  @@@@@@@@  @@@  @@@@ @@@  @@@@@@@\033[0m\n\033[1;31m@@!  @@@  @@! @@! @@!  @@!  @@!@!@@@  @@!  @@@\033[0m     \033[1;32m!@@       @@!  @@@  @@!  @@!@!@@@  !@@\033[0m\n\033[1;31m!@!  @!@  !@! !@! !@!  !@!  !@!!@!@!  !@!  @!@\033[0m     \033[1;32m!@!       !@!  @!@  !@!  !@!!@!@!  !@!\033[0m\n\033[1;31m@!@!@!@!  @!! !!@ @!@  !!@  @!@ !!@!  @!@  !@!\033[0m     \033[1;32m!@!       @!@  !@!  !!@  @!@ !!@!  !!@@!!\033[0m\n\033[1;31m!!!@!!!!  !@!   ! !@!  !!!  !@!  !!!  !@!  !!!\033[0m     \033[1;32m!!!       !@!  !!!  !!!  !@!  !!!   !!@!!!\033[0m\n\033[1;31m!!:  !!!  !!:     !!:  !!:  !!:  !!!  !!:  !!!\033[0m     \033[1;32m:!!       !!:  !!!  !!:  !!:  !!!       !:!\033[0m\n\033[1;31m:!:  !:!  :!:     :!:  :!:  :!:  !:!  :!:  !:!\033[0m     \033[1;32m:!:       :!:  !:!  :!:  :!:  !:!      !:!\033[0m\n\033[1;31m::   :::  :::     ::    ::   ::   ::  ::::: ::\033[0m     \033[1;32m ::: :::  ::::: ::   ::   ::   ::  :::: ::\033[0m\n\033[1;31m :   : :   :      :    :    ::    :    : :  : \033[0m     \033[1;32m :: :: :   : :  :   :    ::    :   :: : :\033[0m\n\033[1;33m @@@@@@@@  @@@@@@@@  @@@  @@@  @@@@@@@@  @@@@@@@    @@@@@@   @@@@@@@   @@@@@@   @@@@@@@\033[0m\n\033[1;33m@@@@@@@@@  @@@@@@@@  @@@@ @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@  @@@@@@@@  @@@@@@@@\033[0m\n\033[1;33m!@@        @@!       @@!@!@@@  @@!       @@!  @@@  @@!  @@@    @@!    @@!  @@@  @@!  @@@\033[0m\n\033[1;33m!@!        !@!       !@!!@!@!  !@!       !@!  @!@  !@!  @!@    !@!    !@!  @!@  !@!  @!@\033[0m\n\033[1;33m!@! @!@!@  @!!!:!    @!@ !!@!  @!!!:!    @!@!!@!   @!@!@!@!    @!!    @!@  !@!  @!@!!@!\033[0m\n\033[1;33m!!! !!@!!  !!!!!:    !@!  !!!  !!!!!:    !!@!@!    !!!@!!!!    !!!    !@!  !!!  !!@!@!\033[0m\n\033[1;33m:!!   !!:  !!:       !!:  !!!  !!:       !!: :!!   !!:  !!!    !!:    !!:  !!!  !!: :!!\033[0m\n\033[1;33m:!:   !::  :!:       :!:  !:!  :!:       :!:  !:!  :!:  !:!    :!:    :!:  !:!  :!:  !:!\033[0m\n\033[1;33m ::: ::::   :: ::::   ::   ::   :: ::::  ::   :::  ::   :::     ::    ::::: ::  ::   :::\033[0m\n\033[1;33m :: :: :   : :: ::   ::    :   : :: ::    :   : :   :   : :     :      : :  :    :   : :\033[0m\n\033[1;35m__By ReYeS\033[0m / \033[1;36mREPLIT_EDITION\033[0m\n")
        while True:
            for index, acc in enumerate(Config().account_list):
                e = acc['email']
                p = acc['password']
                d = acc['device']
                self.generation(e, p, d, index=index)

if __name__ == "__main__":
    os.system("cls" if os.name == 'nt' else "clear")
    Thread(target=run).start()
    try:
        App().run()
    except KeyboardInterrupt:
        os.abort()


"""{
        "email": "sshell-oy3aaawuj@1secmail.org",
        "password": "rogerio123",
        "device": "19EA82A0668AB56525FBDF933B642D020C40892C1CA946AC61888F06A65BD22B40D6E63CEBBEB9BB95",
        "uid": "98239de6-a727-4a45-88b1-ffcd904daf2a",
        "sid": "AnsiMSI6IG51bGwsICIwIjogMiwgIjMiOiAwLCAiMiI6ICI5ODIzOWRlNi1hNzI3LTRhNDUtODhiMS1mZmNkOTA0ZGFmMmEiLCAiNSI6IDE2ODgwODU0MjAsICI0IjogIjE3Ny4xMjcuNzguMTU0IiwgIjYiOiAxMDB9rKii_Az5CYVCG_9Ebixuq24AufA"
    },"""

