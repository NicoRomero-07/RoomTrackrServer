# B7abiertosREST

---

The B7abiertosREST API  aims to provide a easier interface to work with both AEMET OpenData and Malaga's OpenData API. It provides endpoints to:

* Retrieve a bus location given its bus code.
* Retrieve a bus stop given its stop code.
* Proximity search for both bus and stop locations.
* Weather forecast given a day.

## Quick start

It is required to have an [AEMET API](https://opendata.aemet.es/centrodedescargas/altaUsuario?) key in order to have this API up and running. And add it into a .env file with the next content structure:

```txt
AEMET_API_KEY="AEMET_API_KEY"
```

Execute the start.sh and it will install the necessary dependencies and run the API in localhost:8000

```bash
./start.sh
```

## Run the API

```python
uvicorn app.main:app
```

## Test the API

A Postman json file is provided in order to test the API in the root folder.

## Dependencies

```python
pip install -r requirements.txt
```
