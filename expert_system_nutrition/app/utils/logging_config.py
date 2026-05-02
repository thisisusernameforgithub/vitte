# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import RotatingFileHandler


# расширенное логирование
def setup_logging(app):
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler(
        "logs/expert_system.log", maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    error_file_handler = RotatingFileHandler(
        "logs/errors.log", maxBytes=10240, backupCount=10
    )
    error_file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    error_file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Запуск приложения")


class SystemLogger:

    @staticmethod
    def log_ml_event(user_id, input_data, prediction):
        logging.info(
            f"ML_EVENT: User {user_id} requested evaluation for {input_data}. Prediction: {prediction}"
        )

    @staticmethod
    def log_security_event(user_id, action, status):
        logging.warning(
            f"SECURITY: User {user_id} performed {action}. Status: {status}"
        )
