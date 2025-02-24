# MinIO Bootstrap Project

This project sets up buckets and paths inside the MinIO object storage.

## Configuration

Update the `config.py` file with your MinIO configuration details.

## Setup

1. Install Poetry if you haven't already:
    ```sh
    pip install poetry
    ```

2. Install the dependencies:
    ```sh
    poetry install
    ```

3. Run the bootstrap script:
    ```sh
    poetry run python src/main.py
    ```