#!/usr/bin/env python3
import argparse
import glob
import inspect
import json
from pathlib import Path

import pandas as pd

from prep import prep_df

PREDICT_COLUMNS = ["TRANS_ID", "BAN", "IMEI_NO", "primary_email", "f_name", "l_name"]


def _load_transactions(input_path: Path) -> pd.DataFrame:
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError("Input JSON must be a list of transaction objects.")
    if any(not isinstance(item, dict) for item in payload):
        raise ValueError("Input JSON list must contain only objects.")

    return pd.DataFrame(payload)


def _load_optional_csv(prefix: str, empty_columns: list[str]) -> pd.DataFrame:
    matches = sorted(glob.glob(f"{prefix}*.csv"))
    if not matches:
        print(f"WARNING: optional file not found, using empty frame for prefix: {prefix}")
        return pd.DataFrame(columns=empty_columns)

    return pd.read_csv(matches[0])


def _build_predict_payload(df: pd.DataFrame) -> list[dict]:
    for column in PREDICT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    for int_column in ("TRANS_ID", "BAN"):
        df[int_column] = pd.to_numeric(df[int_column], errors="coerce").fillna(0).astype(int)

    return df[PREDICT_COLUMNS].to_dict(orient="records")


def _post_payload(payload: list[dict], predict_url: str | None) -> None:
    from sender import post_to_predict_endpoint

    sig = inspect.signature(post_to_predict_endpoint)
    param_names = list(sig.parameters.keys())
    kwargs = {}

    if "payload" in sig.parameters:
        kwargs["payload"] = payload
    elif param_names:
        kwargs[param_names[0]] = payload

    if predict_url:
        for candidate in ("predict_url", "url", "endpoint_url", "endpoint"):
            if candidate in sig.parameters:
                kwargs[candidate] = predict_url
                break
        else:
            if len(param_names) > 1:
                kwargs[param_names[1]] = predict_url

    response = post_to_predict_endpoint(**kwargs)
    print("Predict response:")
    print(response)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consume raw transaction payload list, run prep_df, and build Swagger /predict payload."
    )
    parser.add_argument("--input", default="input_payload.json", help="Input JSON list file path")
    parser.add_argument(
        "--output",
        default="swagger_payload.json",
        help="Output JSON file path for final /predict payload",
    )
    parser.add_argument("--post", action="store_true", help="POST generated payload to /predict endpoint")
    parser.add_argument("--predict-url", default=None, help="Optional predict endpoint override URL")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    raw_df = _load_transactions(input_path)

    bad_actor = _load_optional_csv("bad_actor", ["BAN"])
    bad_actor_smb = _load_optional_csv("bad_actor_smb", ["BAN"])
    imei_neg = _load_optional_csv("imei_neg", ["ESN", "ENTER_DATE", "SUB_STATUS_RSN_CD"])
    imei_com = _load_optional_csv("imei_com", ["UNIT_ESN"])
    if imei_com.empty:
        coam_fallback = _load_optional_csv("imei_coam", ["UNIT_ESN"])
        if not coam_fallback.empty:
            imei_com = coam_fallback

    prepped_df = prep_df(raw_df, bad_actor, bad_actor_smb, imei_neg, imei_com)
    predict_payload = _build_predict_payload(prepped_df)

    payload_text = json.dumps(predict_payload, indent=2)
    print(payload_text)

    output_path = Path(args.output)
    output_path.write_text(payload_text, encoding="utf-8")
    print(f"Saved Swagger payload to: {output_path}")

    if args.post:
        _post_payload(predict_payload, args.predict_url)


if __name__ == "__main__":
    main()
