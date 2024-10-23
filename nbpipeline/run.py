import papermill as pm
from nbpipeline.config import data_dir, logger
import schedule
import time
from flask import Flask, send_from_directory
import os
import threading
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
from nbformat import read
import io
import traceback
import datetime as dt

 
 

#############################################

def now():
    return dt.datetime.now()

class NBPipeliner():
    def __init__(self, stages, notebooks_dir):
        """
        Initialize the NBPipeliner with the specified pipeline stages and notebooks directory.

        :param stages: A list of tuples, where each tuple contains a notebook name and its corresponding URL.
        :param notebooks_dir: The directory path where the notebooks are stored.
        """
        self.stop_scheduler = None
        self.scheduler_thread = None
         
        self.reports_dir = data_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Reports directory: {self.reports_dir}')
        self.stages = stages

        self.notebooks_dir = notebooks_dir
        logger.info(f'Initialized NBPipeliner with stages: {self.stages}')

        self.status = {}

        for notebook_name, _ in self.stages:
            notebook_path = self.notebooks_dir / f"{notebook_name}.ipynb"
            if not notebook_path.exists():
                logger.fatal(f"Notebook file {notebook_path} does not exist.")
                raise FileNotFoundError(f"Notebook file {notebook_path} does not exist.")


    def job(self):
        """Job to execute notebooks and handle errors."""
        for notebook_name, _ in self.stages:
            logger.info(f"Starting execution of notebook: {notebook_name}")
            if not self.exec_note(notebook_name):
                # TODO: style of error handling must be configurable
                self.stop_scheduler.set()
                break
    
    def _init_routing(self):
        self.app.add_url_rule('/', endpoint='home', view_func=self.generate_task_list_html)

        for notebook_name, url in self.stages:
            self.app.add_url_rule(
                f'/{url}', 
                endpoint=notebook_name,
                view_func=lambda notebook_name=notebook_name: self.serve_stage_results_html(notebook_name)
            )

    def run_scheduler(self):
        """Run the scheduled jobs."""
        while not self.stop_scheduler.is_set():
            schedule.run_pending()
            time.sleep(1)

    
    def start(self):
        

        self.stop_scheduler = threading.Event()        
        # self.job()

        interval_minutes = int(os.environ.get('NBP_DEFAULT_SCHEDULE_INTERVAL_MINUTES', 10))
        logger.debug(f"Scheduler interval set to {interval_minutes} minutes.")
        schedule.every(interval_minutes).minutes.do(self.job)

        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)        
        self.scheduler_thread.start()
        
        self._run_flask()
        

    def _run_flask(self):
        """Main function to set up the scheduler and start the Flask app."""
        self.app = Flask(__name__)
    
        port = int(os.environ.get('NPB_SERVER_PORT', 8088))
        host = str(os.environ.get('NPB_SERVER_HOST', '0.0.0.0'))

        self._init_routing()
        self.app.run(host=host, port=port, use_reloader=False)

    def generate_task_list_html(self):
        """Generate a simple HTML with a list of links for navigation based on PIPELINE_STAGES."""
        links = [
            f'<li><a href="/{url}">{notebook_name}</a> -- {self.status.get(notebook_name)}</li>'
            for notebook_name, url in self.stages if url
        ]

        scheduler_status = (
            "<p>The scheduler is stopped, see error logs</p>"
            if self.stop_scheduler.is_set()
            else (
                f"<p>The scheduler is running, next run scheduled to "
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule.next_run().timestamp()))}</p>"
            )
        )

        html = (
            "<html><body><h1>Logs</h1><ul>" +
            "".join(links) +
            "<h2>Scheduler Status</h2>" +
            scheduler_status +
            "</ul></body></html>"
        )

        return html

    
    def exec_note(self, script_name):
        self.status[script_name] = 'pending'
        """Execute a Jupyter notebook and convert it to HTML."""
        no_error = True
        out_file = self.reports_dir / f'{script_name}.ipynb'
        try:
            self.status[script_name] = 'running', now()
            pm.execute_notebook(
                self.notebooks_dir / f'{script_name}.ipynb',
                out_file,
                log_output=True,
                cwd='notebooks'
            )
            logger.info(f"Notebook {script_name} executed successfully.")
            self.status[script_name] = 'complete', now()
        except Exception as e:
            self.status[script_name] = 'errored', now()
            logger.error(f"Error executing notebook {script_name}: {e}")
            logger.exception(e)
            no_error = False

        self.make_html(out_file)
        return no_error
    

    def serve_stage_results_html(self, html_name):
        return send_from_directory(self.reports_dir, f'{html_name}.html')

    def make_html(self, input_notebook):
        """Convert a Jupyter notebook to HTML."""
        try:
            output_html = self.reports_dir / f'{input_notebook.stem}'

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
            logger.error(f"Error converting notebook to HTML: {e}")
            error_html = (
                "<html><body><h1>Error converting notebook to HTML</h1>"
                f"<pre>{traceback.format_exc()}</pre></body></html>"
            )
            with open(f"{output_html}.html", 'w', encoding='utf-8') as f:
                f.write(error_html)

    


def main():
    __PIPELINE_STAGES = [  # (notebook_name, urls)
        ('sample_stage_1', 'stage1'),
        ('sample_stage_2', 'stage2'),    
    ]
    x = NBPipeliner(__PIPELINE_STAGES, data_dir.parent / 'notebooks')
    x.start()


if __name__ == "__main__":
    main()
