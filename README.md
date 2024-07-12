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