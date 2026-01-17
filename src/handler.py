import csv
import json
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List

import boto3


s3 = boto3.client("s3")


def _summarize_rows(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    # Basic cleaning
    cleaned = []
    for r in rows:
        title = (r.get("title") or "").strip()
        category = (r.get("category") or "").strip()
        if title and category:
            cleaned.append({"title": title, "category": category})

    categories = [r["category"] for r in cleaned]
    counts = Counter(categories)

    top_categories = [{"category": k, "count": v} for k, v in counts.most_common(5)]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "rows_total": len(rows),
        "rows_valid": len(cleaned),
        "unique_categories": len(counts),
        "top_categories": top_categories,
    }


def _read_csv_from_s3(bucket: str, key: str) -> List[Dict[str, str]]:
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8", errors="replace")
    reader = csv.DictReader(body.splitlines())
    return list(reader)


def _write_json_to_s3(bucket: str, key: str, payload: Dict[str, Any]) -> None:
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Expected S3 event (ObjectCreated) or a simplified event:
    {
      "bucket": "my-bucket",
      "key": "input/products.csv"
    }
    Environment variables:
      OUTPUT_BUCKET (optional) - default: input bucket
      OUTPUT_PREFIX (optional) - default: "output/"
    """
    # Support both: real S3 event and simplified event
    if "Records" in event and event["Records"]:
        rec = event["Records"][0]
        bucket = rec["s3"]["bucket"]["name"]
        key = rec["s3"]["object"]["key"]
    else:
        bucket = event.get("bucket")
        key = event.get("key")

    if not bucket or not key:
        return {"statusCode": 400, "body": "Missing bucket/key in event."}

    rows = _read_csv_from_s3(bucket, key)
    summary = _summarize_rows(rows)

    output_bucket = os.getenv("OUTPUT_BUCKET", bucket)
    output_prefix = os.getenv("OUTPUT_PREFIX", "output/")
    output_key = f"{output_prefix.rstrip('/')}/summary.json"

    _write_json_to_s3(output_bucket, output_key, summary)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Summary generated",
                "input": {"bucket": bucket, "key": key},
                "output": {"bucket": output_bucket, "key": output_key},
            },
            indent=2,
        ),
    }
