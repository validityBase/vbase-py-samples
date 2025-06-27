# Multistamper CLI

A command-line tool to stamp multiple files using the vBase API. The tool supports interactive setup of users and collections, and executes a preview + stamping workflow per user.

## Features

- Interactive wizard for setting up users and collections
- Supports multiple users, each with their own `.env` and collections
- Preview mode before stamping
- Optional log output of stamped files
- Directory-based structure for file management

## Folder Structure

```
samples/
└── user_id_1/
    ├── .env                  # Contains API_KEY
    └── collections/
        ├── collection_1/
        │   └── collection_config.json
        └── collection_2/
            └── collection_config.json
```


## File Format Details


## Environment Variable

Set the vBase API endpoint in your local environment or `.env`:

```env
VBASE_API_URL=https://api.vbase.com/stamp
```

## Requirements

- Python 3.7+
- `python-dotenv`

Install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install - r requirements.txt
```

## Usage via CLI

### 1. Setup users and collections via CLI

```bash
python -m multistamper.stamp_cli --setup
```

Prompts for:
- Root folder name (e.g. `samples`)
- User dentifier and their API key
- One or more collections with names and CIDs

> If a folder already exists, it will not be recreated.

### 2. Preview and stamp files via CLI

```bash
python -m multistamper.stamp_cli --users-folder ./samples
```

- Loads all users in the given folder
- Previews files to be stamped
- Prompts: `Do you want to stamp these files?`
- If confirmed, performs stamping via the vBase API

### 3. Save stamp log (optional) via CLI

pyproject.toml
```bash
python -m multistamper.stamp_cli --users-folder ./samples --log-file ./stamp_log.json
```

Writes stamping results to `stamp_log.json`.

## Usage via Notebook

### 1. Preview and stamp files via Notebook

```bash
jupyter notebook
```

## Example Commands

```bash
# Run setup wizard
python -m multistamper.stamp_cli --setup

# Run stamping from configured folder
python -m multistamper.stamp_cli --users-folder ./samples

# Run stamping and save logs
python -m multistamper.stamp_cliy --users-folder ./samples --log-file ./logs.json
```

## Notes

- Skips users without `API_KEY`
- Skips existing folders and configurations
- Outputs detailed previews and confirmations

## Details

### A .env file will be created inside each user folder.

```env
API_KEY=your-vbase-api-key
```

### A collection_config.json file will be created inside each collection folder.

```json
{
  "collection_name": "my_collection",
  "collection_cid": "0xabc123...def"
}
```
