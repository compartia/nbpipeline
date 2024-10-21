import papermill as pm
from nbpipeline.config import data_dir, notebooks_dir
import schedule
import time
from flask import Flask, send_from_directory
import os
import threading
import logging
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
from nbformat import read
import io
import traceback

 
#############################################
# Directory setup
REPORTS_DIR = data_dir / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.info(f'Notebooks directory: {notebooks_dir}')
logging.info(f'Reports directory: {REPORTS_DIR}')

#############################################
PIPELINE_STAGES = [  # (notebook_name, urls)
    ('sample_stage_1', 'stage1'),
    ('sample_stage_1', 'stage2'),    
]
#############################################

stop_scheduler = threading.Event()

#############################################


def generate_navigation_html():
    """Generate a simple HTML with a list of links for navigation based on PIPELINE_STAGES."""
    links = [
        f'<li><a href="/{url}">{notebook_name.replace("_", " ").title()}</a></li>'
        for notebook_name, url in PIPELINE_STAGES if url
    ]

    scheduler_status = (
        "<p>The scheduler is stopped, see error logs</p>"
        if stop_scheduler.is_set()
        else f"<p>The scheduler is running, next run scheduled to "
             f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule.next_run().timestamp()))}</p>"
    )

    html = (
        "<html><body><h1>Rules engine</h1><ul>" +
        "".join(links) +
        "<h2>Scheduler Status</h2>" +
        scheduler_status +
        "</ul></body></html>"
    )

    return html


def make_html(input_notebook):
    """Convert a Jupyter notebook to HTML."""
    try:
        output_html = REPORTS_DIR / f'{input_notebook.stem}'

        # Read the notebook
        with open(input_notebook, 'r', encoding='utf-8') as f:
            notebook_content = f.read()

        # Convert the notebook to HTML
        exporter = HTMLExporter(template_name='lab')
        exporter.exclude_input = True
        output, resources = exporter.from_notebook_node(read(io.StringIO(notebook_content), as_version=4))

        # Write the HTML output to a file
        writer = FilesWriter()
        writer.write(output, resources, str(output_html))

    except Exception as e:
        logging.error(f"Error converting notebook to HTML: {e}")
        error_html = (
            "<html><body><h1>Error converting notebook to HTML</h1>"
            f"<pre>{traceback.format_exc()}</pre></body></html>"
        )
        with open(f"{output_html}.html", 'w', encoding='utf-8') as f:
            f.write(error_html)


def exec_note(script_name):
    """Execute a Jupyter notebook and convert it to HTML."""
    no_error = True
    out_file = REPORTS_DIR / f'{script_name}.ipynb'
    try:
        pm.execute_notebook(
            notebooks_dir / f'{script_name}.ipynb',
            out_file,
            log_output=True,
            cwd='notebooks'
        )
        logging.info(f"Notebook {script_name} executed successfully.")
    except Exception as e:
        logging.error(f"Error executing notebook {script_name}: {e}")
        logging.exception(e)
        no_error = False

    make_html(out_file)
    return no_error


def job():
    """Job to execute notebooks and handle errors."""
    for notebook_name, _ in PIPELINE_STAGES:
        if not exec_note(notebook_name):
            stop_scheduler.set()
            break


def run_scheduler():
    """Run the scheduled jobs."""
    while not stop_scheduler.is_set():
        schedule.run_pending()
        time.sleep(1)


def serve_stage_results_html(html_name):
    return send_from_directory(REPORTS_DIR, f'{html_name}.html')


def _init_routing(app):
    app.add_url_rule('/', endpoint='home', view_func=generate_navigation_html)

    for notebook_name, url in PIPELINE_STAGES:
        app.add_url_rule(f'/{url}', endpoint=notebook_name,
                         view_func=lambda notebook_name=notebook_name: serve_stage_results_html(notebook_name))


def main():
    """Main function to set up the scheduler and start the Flask app."""
    app = Flask(__name__)

    interval_minutes = int(os.environ.get('SCHEDULE_INTERVAL_MINUTES', 10))
    schedule.every(interval_minutes).minutes.do(job)

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    port = int(os.environ.get('RULES_ENGINE_PORT', 8088))
    host = str(os.environ.get('RULES_ENGINE_HOST', '0.0.0.0'))

    _init_routing(app)

    app.run(host=host, port=port, use_reloader=False)


if __name__ == "__main__":
    # job()
    main()
