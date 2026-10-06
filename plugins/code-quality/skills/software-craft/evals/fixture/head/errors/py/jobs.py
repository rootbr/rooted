"""Plugin configuration loading and the background job runner."""
import json
import logging

log = logging.getLogger(__name__)


def load_plugin_config_catches_everything(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def run_queued_jobs_isolating_failures(queue):
    for job in queue.drain():
        try:
            job.run()
        except Exception:
            # isolation point: one failed job must not stop the independent jobs queued after it
            log.exception("job %s failed", job.id)
