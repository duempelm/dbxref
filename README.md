# DBxRef
This project was heavily inspired by [https://github.com/lukasjelonek/dbxref](https://github.com/lukasjelonek/dbxref).
It is a small project to test [FastHTML](https://www.fastht.ml).

The DBxRef is a small service, allowing to parse ids into a weblink and either resolve it or redirect to that website.
Therefore the service allow the configuration of an *config.json* file.

# Getting Started
Download the repository:
```bash
git clone git@github.com:duempelm/dbxref.git
```

Initalize the environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Running tests:
```bash
python3 main.test.py
```

Starting service:
```bash
python3 main.py
```

Listen to what the service tell you or try to access the service under this address: [http://localhost:4000](http://localhost:4000)

To deactivate the environment:
```bash
deactivate
```

# Configuration
The configuration file contains a python regexp and an modified html link. The regexp is used to check if a given id resembles to an webservice. If so the service replaces the '$' in the html link and redirect to it.
```json
[
  {
    "regexp": "GO:\\d{7}",
    "html": "https://www.ebi.ac.uk/QuickGO/term/$"
  },
  {
    "regexp": "IPR\\d{6}",
    "html": "https://www.ebi.ac.uk/interpro/entry/InterPro/$"
  }
]
```

Make sure when using the service to configure all links and regular expressions to your needs.

# API
While the service provides an UI, it also offers a minimalistic REST-API.

### '/'
The homescreen of the application.

### 'GET /config'
Response the json of the config file as a formatted string.

### 'GET /resolve?id=string'
Receives an id as string and response the address of the webresource if id matches any of the configured regular expressions.

### 'GET /redirect?id=string'
Receives an id as string and redirect to the webresource if id matches any of the configured regular expressions.
