# AppController Consumer Script

This repository now includes a Python consumer script to show how transaction input is consumed and prepared for the `/predict` API.

## Files

- `consume_and_prepare_for_swagger.py`: Reads input JSON transactions, runs `prep_df` (without changing `prep.py`), creates Swagger-ready `/predict` payload, saves `swagger_payload.json`, and can optionally call the endpoint.
- `input_payload.json`: Sample input list containing multiple transactions.

## Input format

The script expects a JSON list of transaction objects:

```json
[
  {
    "BAN": 847362910,
    "TRANS_ID": 100042,
    "IMEI_NO": "358743081234567"
  }
]
```

## Run locally

```bash
python consume_and_prepare_for_swagger.py --input-json input_payload.json
```

This writes `swagger_payload.json` in `/predict` request format:

```json
[
  {
    "TRANS_ID": 100042,
    "BAN": 847362910,
    "IMEI_NO": "358743081234567",
    "primary_email": "...",
    "f_name": "...",
    "l_name": "..."
  }
]
```

## Optional endpoint call

```bash
python consume_and_prepare_for_swagger.py \
  --input-json input_payload.json \
  --endpoint-url http://localhost:9000/predict
```

## Optional CSV fallbacks when files are missing

The script safely passes empty DataFrames with required columns if optional files are absent:

- `bad_actor_data_decrypted.csv` -> `BAN`
- `bad_actor_smb_decrypted.csv` -> `BAN`
- `imei_neg_frd_decrypted.csv` -> `ESN`, `ENTER_DATE`, `SUB_STATUS_RSN_CD`
- `imei_coam_frd_decrypted.csv` -> `UNIT_ESN`

This prevents crashes in `prep_df` when optional CSVs are unavailable.
