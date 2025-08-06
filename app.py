#!/usr/bin/env python3
"""Simple Flask web server for a micro-services application."""
import logging
from typing import Dict, Any
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

# Configure logging for observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/health", methods=["GET"])
def health_check() -> Dict[str, Any]:
    """Return health status of the application."""
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "message": "Application is running"})


@app.route("/", methods=["GET"])
def index() -> Dict[str, Any]:
    """Return a welcome message."""
    logger.info("Index endpoint requested")
    return jsonify({"message": "Welcome to the micro-services demo!"})


def main() -> None:
    """Main entry point for the application."""
    logger.info("Starting Flask application")
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
