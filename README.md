# ☁️ AWS Lambda CSV Summary (Serverless Data Pipeline)

Serverless pipeline that generates a JSON summary from a CSV file uploaded to Amazon S3.

**Flow:**
S3 (`input/*.csv`) → Lambda (Python) → S3 (`output/summary.json`)

The repo also includes a local runner so the logic can be tested without AWS.

---

## ✨ Features
- Reads CSV with columns: `title`, `category`
- Cleans invalid rows
- Computes category stats (top categories)
- Writes `summary.json` with UTC timestamp
- Works locally and on AWS (S3 + Lambda trigger)

---

## 📁 Project Structure
```
aws-lambda-csv-summary/
│
├── src/
│   ├── handler.py          # AWS Lambda handler (S3 -> JSON)
│   └── local_runner.py     # Local execution (no AWS needed)
│
├── data/
│   └── sample_input.csv
│
└── events/
    └── s3_event.json       # simplified manual test event

```
---

## ▶️ Run Locally (Windows)
```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m src.local_runner
```

Output:
- `output/summary.json` (generated locally)

---

## 🚀 Deploy on AWS (Console)

### 1) S3
- Create a bucket in the same region as the Lambda function
- Create folders:
  - `input/`
  - `output/`
- Upload a CSV to: `input/products.csv`

### 2) IAM Role for Lambda
Grant permissions:
- `s3:ListBucket` on `arn:aws:s3:::YOUR_BUCKET`
- `s3:GetObject`, `s3:PutObject` on `arn:aws:s3:::YOUR_BUCKET/*`

### 3) Lambda
- Runtime: Python 3.11/3.12
- Upload a ZIP containing:
  - `src/`
  - `lambda_function.py` (exports `lambda_handler`)
- Handler:
  - `lambda_function.lambda_handler`

### 4) Trigger
Create an S3 event notification (recommended from S3 → Properties):
- Event: ObjectCreated
- Prefix: `input/`
- Suffix: `.csv`
- Destination: your Lambda function

---

## ✅ Result
Uploading a CSV in `input/` generates:
- `output/summary.json`
