# yama

Yama is the resume generation subnet.

TODO: Finalize this document, i.e. make sure all steps are included.

## Configuration

Create a `.env` file by copying the example environment file `.env.example`:
```bash
cp .env.example .env
```

## Validator

### .env
| env var | description | required |
|---------|-------------|----------|
| `KEY_NAME` | The name of the key registered as a module | ✅ |
| `TESTNET` | `0` to run on mainnet, `1` to run on testnet (default: `0`) | ❌ |
| `NETUID` | The netuid of the subnet | ✅ |
| `VALIDATOR_INTERVAL` | The time between validator steps (default: `10`) | ❌ |

### Dependencies

Install python requirements:
```bash
python -m pip install -r requirements.txt
```

Install the `en_core_web_trf` model:
```bash
python -m spacy download en_core_web_trf
```

Install the project in editable mode:
```bash
python -m pip install -e .
```