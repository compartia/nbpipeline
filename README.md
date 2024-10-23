[![Python Package](https://github.com/compartia/nbpipeline/actions/workflows/python-publish.yml/badge.svg)](https://github.com/compartia/nbpipeline/actions/workflows/python-publish.yml)

 

# NBPipeliner lite (to be renamed to NBPipelite)

**NBPipeliner** is a Python library designed to automate the execution of Jupyter notebooks, convert them to HTML reports, and serve them via a Flask web application. It also includes scheduling capabilities to run notebooks at regular intervals.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)


## Features

- **Automated Notebook Execution:** Execute Jupyter notebooks using Papermill.
- **HTML Conversion:** Convert executed notebooks to HTML reports using nbconvert.
- **Web Serving:** Serve HTML reports via a Flask web application.
- **Scheduling:** Schedule notebook executions at configurable intervals.
- **Logging:** Comprehensive logging for monitoring and debugging.

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

### 1. **Clone the Repository**

```bash
git clone https://github.com/compartia/nbpipeline.git
cd nbpipeliner
```

### 2. **Install Dependencies**

Ensure you have Poetry installed. If not, install it using:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then, install the project's dependencies:

```bash
poetry install
```

### 3. **Activate the Virtual Environment**

Activate Poetry's virtual environment:

```bash
poetry shell
```

## Configuration

NBPipeliner can be configured using environment variables. Below are the available configurations:

| Environment Variable                        | Description                                                       | Default Value |
|---------------------------------------------|-------------------------------------------------------------------|---------------|
| `NBP_LOG_LEVEL`                                 | Logging level for console output                                 | `INFO`        |
| `NBP_LOG_LEVEL_FILE`                            | Logging level for file output                                    | `INFO`        |
| `NBP_DEFAULT_SCHEDULE_INTERVAL_MINUTES`     | Interval in minutes between scheduled notebook executions        | `10`          |
| `NPB_SERVER_PORT`                           | Port number for the Flask web server                             | `8088`        |
| `NPB_SERVER_HOST`                           | Host address for the Flask web server                            | `0.0.0.0`     |
| `NPB_WORK_DIR`                                  | Base directory for data (reports)                  | `./data`      |

### Setting Environment Variables

You can set environment variables in your shell or use a `.env` file with tools like [python-dotenv](https://github.com/theskumar/python-dotenv).

**Example:**

```bash
export LOG_LEVEL=DEBUG
export NPB_SERVER_PORT=5000
```

## Usage

### 1. **Prepare Notebooks**


Ensure that your Jupyter notebooks are placed in the `notebooks_dir` directory. The names of these notebooks should match the names defined in your pipeline stages. This ensures that each stage can correctly locate and execute the corresponding notebook.

For example, if you have a stage defined as `('sample_stage_1', 'stage1')`, there should be a notebook named `sample_stage_1.ipynb` in your `notebooks_dir` directory.


### 2. **Define Pipeline Stages**

Define your pipeline stages. Each stage is a tuple containing the notebook name and the URL path.

```python
    from nbpipeline.run import NBPipeliner

    PIPELINE_STAGES = [  
        ('sample_stage_1', 'stage1'),
        ('sample_stage_2', 'stage2'),    
    ]
    pipeline = NBPipeliner(__PIPELINE_STAGES, notebooks_dir)
    pipeline.start()
```

### 3. **Run your Application**

Upon running, the application will:

- Execute the defined Jupyter notebooks.
- Convert them to HTML reports.
- Serve the reports via a Flask web application accessible at `http://<host>:<port>/`.

### 4. **Access the Reports**

Open your web browser and navigate to `http://localhost:8088/` (replace `8088` with your configured port). You'll see a navigation page listing all the reports. Click on any link to view the corresponding HTML report.

### 5. **Scheduling**

The pipeline is scheduled to execute notebooks at intervals defined by `NBP_DEFAULT_SCHEDULE_INTERVAL_MINUTES`. By default, it's set to run every 10 minutes. You can adjust this interval by setting the environment variable accordingly.

**Example:**

To schedule the pipeline to run every 30 minutes:

```bash
export NBP_DEFAULT_SCHEDULE_INTERVAL_MINUTES=30
```

 
- **data/reports/**: Generated HTML reports will be saved here.


 
---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [MIT License](LICENSE).
