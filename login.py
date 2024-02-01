import main
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode, quote, unquote
from flask import redirect, session, url_for, request

app = main.app

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id="tDexqyish6TMN6vBOk418s2ryMP9vNxI",
    client_secret="V6ezgf5X8mBIpu3xqN9ginSTlVho7j3klp5SLfo46dyqSaagNoqoSXBmlqGQQwt0",
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://dev-d02ogu7kni6jedsw.us.auth0.com/.well-known/openid-configuration'
)


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True, url=request.args.get("url"))
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    url = request.args.get("url")
    return redirect(url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://dev-d02ogu7kni6jedsw.us.auth0.com/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("redirects", url=quote(request.args.get("url")), _external=True),
                "client_id": "tDexqyish6TMN6vBOk418s2ryMP9vNxI",
            },
            quote_via=quote_plus,
        )
    )


@app.route("/redirects")
def redirects():
    url = unquote(request.args.get("url"))
    return redirect(url)
