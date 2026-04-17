from __future__ import annotations

import argparse
import json
import socket
from pathlib import Path
from typing import Any
from urllib import error, request

import pandas as pd

PREDICT_COLUMNS = ["TRANS_ID", "BAN", "IMEI_NO", "primary_email", "f_name", "l_name"]


def _read_optional_csv(path: Path, expected_columns: list[str]) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, sep=",", encoding="latin1", low_memory=False)
    return pd.DataFrame(columns=expected_columns)


def _load_transactions(input_json: Path) -> pd.DataFrame:
    with input_json.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        raise ValueError("Input JSON must be a list of transaction objects")

    return pd.DataFrame(payload)


def _build_predict_payload(df: pd.DataFrame, max_records: int | None) -> list[dict[str, Any]]:
    payload_df = df if max_records is None else df.head(max_records)
    payload_df = payload_df.copy()

    for column in PREDICT_COLUMNS:
        if column not in payload_df.columns:
            payload_df[column] = None

    for column in ["TRANS_ID", "BAN"]:
        if column in payload_df.columns:
            payload_df[column] = pd.to_numeric(payload_df[column], errors="coerce").fillna(0).astype(int)

    return payload_df[PREDICT_COLUMNS].to_dict(orient="records")


def _post_predict(endpoint_url: str, payload_records: list[dict[str, Any]], timeout: int) -> dict[str, Any]:
    req = request.Request(
        endpoint_url,
        data=json.dumps(payload_records, default=str).encode("utf-8"),
        headers={"accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"status_code": resp.status, "response_body": body}
    except error.HTTPError as http_err:
        body = http_err.read().decode("utf-8", errors="replace")
        return {"status_code": http_err.code, "response_body": body}
    except error.URLError as url_err:
        return {"status_code": None, "response_body": f"URLError: {url_err}"}
    except (socket.timeout, TimeoutError):
        return {
            "status_code": None,
            "response_body": f"Request to prediction endpoint timed out after {timeout} seconds",
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume JSON transactions, run prep_df, and build Swagger-ready /predict payload."
    )
    parser.add_argument("--input-json", default="input_payload.json", help="Path to input JSON list of transactions")
    parser.add_argument("--output-json", default="swagger_payload.json", help="Path to write /predict payload JSON")
    parser.add_argument("--max-records", type=int, default=None, help="Optional max rows to include in output payload")
    parser.add_argument("--endpoint-url", default=None, help="Optional /predict endpoint URL to call")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds for endpoint call")
    parser.add_argument("--bad-actor-csv", default="bad_actor_data_decrypted.csv")
    parser.add_argument("--bad-actor-smb-csv", default="bad_actor_smb_decrypted.csv")
    parser.add_argument("--imei-neg-csv", default="imei_neg_frd_decrypted.csv")
    parser.add_argument("--imei-com-csv", default="imei_coam_frd_decrypted.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        from prep import prep_df
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Could not import prep_df from prep.py. Ensure prep.py is available on PYTHONPATH."
        ) from exc

    raw_df = _load_transactions(Path(args.input_json))

    bad_actor = _read_optional_csv(Path(args.bad_actor_csv), ["BAN"])
    bad_actor_smb = _read_optional_csv(Path(args.bad_actor_smb_csv), ["BAN"])
    imei_neg = _read_optional_csv(Path(args.imei_neg_csv), ["ESN", "ENTER_DATE", "SUB_STATUS_RSN_CD"])
    imei_com = _read_optional_csv(Path(args.imei_com_csv), ["UNIT_ESN"])

    (
        processed_df,
        _bad_actor_set,
        _bad_actor_smb_set,
        _imei_neg_set,
        _imei_com_set,
    ) = prep_df(raw_df, bad_actor, bad_actor_smb, imei_neg, imei_com)
    predict_payload = _build_predict_payload(processed_df, args.max_records)

    output_path = Path(args.output_json)
    output_path.write_text(json.dumps(predict_payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {len(predict_payload)} records to {output_path}")

    if args.endpoint_url:
        response = _post_predict(args.endpoint_url, predict_payload, args.timeout)
        print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
