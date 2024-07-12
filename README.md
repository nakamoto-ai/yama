# yama

Yama is the resume generation subnet.

TODO: Finalize this document, i.e. make sure all steps are included.

## Validator

### Environment Variables
| environment variable | description                                                 | required |
|----------------------|-------------------------------------------------------------|----------|
| `KEY_NAME`           | The name of the key registered as a module                  | ✅       |
| `TESTNET`            | `0` to run on mainnet, `1` to run on testnet (default: `0`) | ❌       |
| `NETUID`             | The netuid of the subnet                                    | ✅       |
| `VALIDATOR_INTERVAL` | The time between validator steps (default: `10`)            | ❌       |

These environment variables can be set in two ways: using a `.env` file and setting environment variables directly.

#### .env file
Create a `.env` file by copying the example environment file `.env.example` to your desired path:
```bash
cp .env.example <path-to-env-file>
```

Then insert the values of each into the `.env` file.

#### Directly Setting Environment Variables
Set each of the environment variables directly. This can be done by executing an `export` statement for each, or appending each `export` statement to your `.bashrc` file.

Example export statement:
```bash
export KEY_NAME=my-wallet
```

When running the validator make sure to pass `--ignore-env-file` so that it accesses these values directly.

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

### Running

The validator accepts two different command line arguments relating to the environment.

#### CLI Arguements

| argument            | description                                            | required |
|---------------------|--------------------------------------------------------|----------|
| `--env`             | The path to your `.env` file (default: `.env`)         | ❌       |
| `--ignore-env-file` | If passed, the validator will not load the `.env` file | ❌       |

To execute the program with python, run the following:
```bash
python src/validator/main.py [--env <env-file-path> | --ignore-env-file]
```

Alternatively, you can run the program in the background using `pm2`:
```bash
pm2 start src/validator/main.py --interpreter python --name validator -- [--env <env-file-path> | --ignore-env-file]
```

## Miner

### Miners
* [NLTK Miner](#How-To-run-the-nltk-miner)
* [Huggingface T5 Miner](#How-To-run-the-hf_t5-miner)

## How to run the NLTK miner:

### Hardware requirements

Recommended requirements

    CPU: 4-core Intel i5 or equivalent AMD processor, 2.5 GHz-3.5 GHz
    RAM: 8 GB or more
    Storage: 20 GB SSD
    GPU: Not required
    Network: Broadband internet connection


> [!NOTE]
> Requires Python 3.8 or newer

1) Clone project

`git clone https://github.com/nakamoto-ai/yama`

2) Create virtual environment

```
cd yama
python -m venv venv
source venv/bin/activate
```

3) Install dependencies

`pip install -r requirements.txt`

4) Register the miner

`comx module register <name> <your_commune_key> --netuid [NETUID] --ip <your_ip> --port <your_port>`

6) Run the miner

```
python src/yama/miner/main.py --miner nltk
```

(Optional) Run with pm2 

```
sudo apt install jq -y && sudo apt install npm -y && sudo npm install pm2 -g && pm2 update
pm2 start --name yama-nltk "python src/yama/miner/main.py --miner nltk"
```

## How To run the HF_T5 miner:

### Hardware Requirements

Recommended Requirements:

    CPU: 6-core Intel i7 or equivalent AMD processor, 3.0 GHz or higher
    RAM: 16 GB or more
    Storage: 20 GB SSD
    GPU: NVIDIA GPU with at least 6 GB VRAM (e.g., GTX 1060 or better)
    Network: Broadband internet connection

> [!NOTE]
> Requires Python 3.8 or newer and PyTorch

1) Clone project

`git clone https://github.com/nakamoto-ai/yama`

2) Create virtual environment

```
cd yama
python -m venv venv
source venv/bin/activate
```

3) Install dependencies

`pip install -r requirements.txt`

4) Register the miner

`comx module register <name> <your_commune_key> --netuid [NETUID] --ip <your_ip> --port <your_port>`

6) Run the miner

```
python src/yama/miner/main.py --miner t5
```

(Optional) Run with pm2 

```
sudo apt install jq -y && sudo apt install npm -y && sudo npm install pm2 -g && pm2 update
pm2 start --name yama-t5 "python src/yama/miner/main.py --miner t5"
```
