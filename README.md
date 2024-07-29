# Yama Subnet: Revolutionizing Recruitment and Resume Management

The Yama subnet is a cutting-edge system dedicated to enhancing the recruitment process by seamlessly generating resumes and assessing their alignment with job descriptions (JDs). The subnet aims to be a one-stop destination for all hiring needs, generating resumes and producing ATS scores for given job descriptions.

## Functions

- Validators: Validators generate JDs from the corpus, which is created from data scraped from various job sites and existing datasets. They pass these JDs to the miners and subsequently evaluate the resumes generated by the miners. Validators score the miners' output and determine if the resumes meet the required threshold, responding with a "shortlisted" or "not shortlisted" decision.
  
- Miners: Miners receive JDs from validators and generate high-quality resumes that match the job descriptions. They also provide ATS (Applicant Tracking System) scores for these resumes to ensure alignment with the specific requirements of the JDs.

## Core Features

1. Data Scraping and Corpus Creation: Yama gathers data from various job sites and existing datasets to create a comprehensive corpus for generating job descriptions and resumes.
2. Resume Generation: Miners produce tailored resumes by analyzing the provided JDs, ensuring they fit the job requirements.
3. ATS Framework: Yama includes an ATS framework that extracts skills from JDs and performs several analytical tasks:
   - Segmentation & Entity Recognition: Identifying and segmenting entities within the JD.
   - Normalization: Ensuring consistency in the data.
   - Keyword Tagging: Tagging related keywords to enhance matching accuracy.
   - Scoring Metric: Providing a scoring mechanism to evaluate resume fit against the JD.

## Process Flow

1. Data Collection: Scraping data from job sites and utilizing existing datasets to build the corpus.
2. Validation: Validators pre-process the data, and generate JDs.
3. Mining: Miners generate resumes based on the JDs.
4. Feedback Loop: Validators score the miners' responses and provide feedback ("shortlisted" or "not shortlisted") based on a predefined threshold to ensure continuous improvement.

## Product

Introducing **Yama** – the ultimate tool for streamlining the resume creation and evaluation process. Yama offers two powerful features designed to enhance both the job application and hiring experience:

1. ATS Checker: Upload resumes and job descriptions to receive a detailed score, ensuring candidates' resumes align perfectly with job requirements.
2. Resume Generation: Simply attach a job description and fill in your skills to generate a customized resume tailored specifically for that job.

For Students: Yama provides a streamlined path to create professional resumes that stand out in the competitive job market.
For Companies: Yama offers precise tools for evaluating candidate resumes, making the hiring process more efficient and effective.
For Recruiters: Yama serves as a comprehensive solution for managing and assessing large volumes of resumes quickly and accurately, helping you find the best candidates with ease.

## Leaderboard

https://huggingface.co/spaces/samNakamoto/yama-leaderboard 


## Validator

### Hardware Requirements
```yaml
CPU: 8 cores
GPU: False
RAM: 16GB
Storage: 30GB
```

### Cloning
To get started, clone the repository.

```bash
git clone https://github.com/nakamoto-ai/yama.git
```

### Environment Variables
| environment variable | description                                                 | required |
|----------------------|-------------------------------------------------------------|----------|
| `KEY_NAME`           | The name of the key registered as a module                  | ✅       |
| `TESTNET`            | `0` to run on mainnet, `1` to run on testnet (default: `0`) | ❌       |
| `NETUID`             | The netuid of the subnet                                    | ✅       |
| `VALIDATOR_INTERVAL` | The time between validator steps (default: `10`)            | ❌       |

These environment variables can be set in two ways: using a `.env` file or setting environment variables directly.

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
python -m pip install -r validator_requirements.txt
```

Install the `en_core_web_trf` model:
```bash
python -m spacy download en_core_web_trf
```

Install the `en_core_web_md` model:
```bash
python -m spacy download en_core_web_md
```

Install the project in editable mode:
```bash
python -m pip install -e .
```

### Running

The validator accepts two different command line arguments relating to the environment.

#### CLI Arguments

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

`pip install -r nltk_miner_requirements.txt`

Install the project in editable mode:

```bash
pip install -e .
```

4) Register the miner

`comx module register <name> <your_commune_key> --netuid [NETUID] --ip <your_ip> --port <your_port>`

5) Create and set environment variables in a .env file

Create a `.env` file by copying the example environment file `.env.example`:
```bash
cp .env.example .env
```

Then insert your key name values of each into the `.env` file.

```
KEY_NAME=<your_commune_key>
```

6) Run the miner

```
python src/miner/main.py --miner nltk
```

(Optional) Run with pm2 

```
sudo apt install jq -y && sudo apt install npm -y && sudo npm install pm2 -g && pm2 update
pm2 start --name yama-nltk "python src/miner/main.py --miner nltk"
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

`pip install -r t5_miner_requirements.txt`

Install the project in editable mode:

```bash
pip install -e .
```

4) Register the miner

`comx module register <name> <your_commune_key> --netuid [NETUID] --ip <your_ip> --port <your_port>`

5) Create and set environment variables in a .env file

Create a `.env` file by copying the example environment file `.env.example`:
```bash
cp .env.example .env
```

Then insert your key name values of each into the `.env` file.

```
KEY_NAME=<your_commune_key>
```

6) Run the miner

```
python src/miner/main.py --miner t5
```

(Optional) Run with pm2 

```
sudo apt install jq -y && sudo apt install npm -y && sudo npm install pm2 -g && pm2 update
pm2 start --name yama-t5 "python src/miner/main.py --miner t5"
```
