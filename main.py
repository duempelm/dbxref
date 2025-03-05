#IMPORT
from fasthtml.common import *
import json
import re
from urllib3 import request

#FUNCTIONS
def load_config():
    """
    Loads the config.json file and returns it content.

    Returns:
        list: List of dicts with the structure {"regexp": "", "html": ""}.
    """
    try:
        with open('config.json', 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        print("The file 'config.json' was not found.")
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)

def resolve_id(id):
    """
    Compares each config.json entry's 'regexp' value with an given 'id' string and replaces the '$' character in the 'html' value with the id if the 'regexp' match.

    Parameters:
        id (string): String to resolve.

    Returns:
        string | None: Returns the modified 'html', if a 'regexp' value matches the 'id' string. Returns None, if none of the 'regexp' values match with the 'id' string.
    """
    conf_data = load_config()

    for c in conf_data:
        print(c)
        if re.search(c["regexp"], id):
            replaced_html = c["html"].replace("$", id)
            return replaced_html
    return None

def available(link):
    """
    GET requests an website behind a 'link' string and returns the status of the response.

    Parameters:
        link (string): HTML Link to an website.

    Returns:
        integer: Status code of the response
    """
    res = request("GET", link)
    return res.status


#FASTHTML ####################################################################################################
app, rt = fast_app(pico=False)

#CSS
custom_style = Style("""
    body {
        font-family: Arial, sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
        background-image: url('/assets/squares_background.png');
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 60%;
        overflow: hidden;
    }
    body::before {
            content: "";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60%;
            height: 100%;
            background: radial-gradient(circle, transparent 20%, rgba(255,255,255,0.8) 80%);
            background-color: rgba(255, 255, 255, 0.7);
            pointer-events: none;
            z-index: -1;
        }
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 800px;
        position: relative;
        z-index: 1;
    }
    h1 {
        color: #0759E4;
        font-size: 48px;
        margin-bottom: 30px;
        text-align: center;
    }
    .search-container {
        display: flex;
        width: 100%;
        margin-bottom: 30px
    }
    input {
        flex-grow: 1;
        min-width: 600px;
        padding: 10px 20px;
        font-size: 16px;
        border: 1px solid #dfe1e5;
        border-radius: 24px 0 0 24px;
        outline: none;
    }

    .search-button {
        width: 100px;
        padding: 10px;
        font-size: 16px;
        background-color: #4285F4;
        color: white;
        border: none;
        border-radius: 0 24px 24px 0;
        cursor: pointer;
    }
    .search-button:hover {
        background-color: #1A69EF;
    }

    .config-button {
        width: 100px;
        padding: 10px;
        font-size: 16px;
        background-color: white;
        color: #4285F4;
        border: 1px solid #4285F4;
        border-radius: 24px;
        cursor: pointer;
        margin-bottom: 15%
    }
    .config-button:hover {
        background-color: #95BAF9;
    }
""")

#HTML
@rt("/")
def home():
    """Homescreen"""
    return Titled("DBxRef",
        custom_style,
        Main(
            Form(
                Div(
                    Input(name="id", placeholder="Enter ID (e.g. 'GO:0005515')", required=True, aria_label="Enter ID such as 'GO:0005515'"),
                    Button("Go", type="submit", cls="search-button", aria_label="Submit search"),
                    cls="search-container"
                ),
                action="/redirect",
                method="GET",
            ),
            Button("Config", hx_get="/config", hx_push_url="true", hx_target="body", cls="config-button", aria_label="Show config json"),
            cls="container"
        )
    )

@rt("/redirect", methods=["GET"])
def redirect(id: str):
    """Redirects to link if resolve_id succesful and the resource is available; else shows an page with error text."""
    link = resolve_id(id)
    if not link:
        return Pre(f"No related webpage found for '{id}'!\nCheck \\config to see available resources.", id="json-content")
    status = available(link)

    if status >= 400:
        return Pre(f"Not available [{status}]!", id="json-content")
    else:
        return Redirect(link)


@rt("/resolve", methods=["GET"])
def resolve(id: str):
    """Shows link if resolve_id succesful and the resource is available; else shows an page with error text."""
    link = resolve_id(id)
    if not link:
        return Pre(f"No related webpage found for '{id}'!\nCheck \\config to see available resources.", id="json-content")
    status = available(link)

    if status >= 400:
        return Pre(f"Not available [{status}]!", id="json-content")
    else:
        return Pre(link, id="json-content")


@rt("/config")
def config():
    """Shows the content of the config.json file."""
    conf_data = load_config()
    formatted_conf_data = json.dumps(conf_data, indent=2)
    return Pre(formatted_conf_data, id="json-content")


serve()
