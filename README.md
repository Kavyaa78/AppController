# Consumer payload workflow

This repo includes `consume_and_predict.py` to convert a raw incoming transaction payload (JSON list) into the final request body expected by Swagger `POST /predict`.

## Run in a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas requests
python consume_and_predict.py --input input_payload.json
```

The script:
- validates the input JSON is a list of objects
- runs `prep_df(...)`
- builds the 6-column `/predict` payload
- prints JSON to stdout
- writes `swagger_payload.json`

## Paste into Swagger `POST /predict`

1. Run `python consume_and_predict.py --input input_payload.json`.
2. Copy the printed JSON array (or open `swagger_payload.json`).
3. Paste that array into Swagger request body for `POST /predict`.
4. Execute.

> Note: `/predict` consumes only the final 6 columns:
> `TRANS_ID`, `BAN`, `IMEI_NO`, `primary_email`, `f_name`, `l_name`.
> Your input payload may include extra raw fields required for preprocessing.

## Optional direct POST

If you want the script to call the endpoint directly:

```bash
python consume_and_predict.py --input input_payload.json --post
```

You can optionally override URL if supported by your sender function signature:

```bash
python consume_and_predict.py --input input_payload.json --post --predict-url "http://localhost:8080/predict"
```
