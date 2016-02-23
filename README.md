# Setup

Ensure you have `easy_install`, `pip` , `virtualenv` and `postgres` installed at a system level.

Ensure you have `make` on your system.

Ensure you have AWS credentials on your system for the `frontend` account.

## Python Environment

To setup a local python environment in this context:


```bash
virtualenv .

```

Then change into the context of the environment with:

```bash
source bin/activate
```

### Python Dependencies

Now you need to install the python dependencies.

```bash
pip install -r requirements.txt
```

### Make runnable lambda function

Assuming you have `make` on your system, run

```bash
make build
```

This will now create a `dist/` directory with the exact structure of how the lambda function should be laid out, also in here is the `function.zip` file that can be used to upload to lambda.
