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

## Usage

### 1. Setup users and collections

```bash
python stamp_cli.py --setup
```

Prompts for:
- Root folder name (e.g. `samples`)
- User dentifier and their API key
- One or more collections with names and CIDs

> If a folder already exists, it will not be recreated.

### 2. Preview and stamp files

```bash
python stamp_cli.py --users-folder ./samples
```

- Loads all users in the given folder
- Previews files to be stamped
- Prompts: `Do you want to stamp these files?`
- If confirmed, performs stamping via the vBase API

### 3. Save stamp log (optional)

```bash
python stamp_cli.py --users-folder ./samples --log-file ./stamp_log.json
```

Writes stamping results to `stamp_log.json`.

## File Format Details

### .env (per user folder)

```env
API_KEY=your-vbase-api-key
```

### collection_config.json (per collection folder)

```json
{
  "collection_name": "my_collection",
  "collection_cid": "0xabc123...def"
}
```

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
pip install python-dotenv
```

## Example Commands

```bash
# Run setup wizard
python stamp_cli.py --setup

# Run stamping from configured folder
python stamp_cli.py --users-folder ./samples

# Run stamping and save logs
python stamp_cli.py --users-folder ./samples --log-file ./logs.json
```

## Notes

- Skips users without `API_KEY`
- Skips existing folders and configurations
- Outputs detailed previews and confirmations