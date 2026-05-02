# -*- coding: utf-8 -*-
from app.ml_model import RationEvaluator
import os


def test_ml_evaluator_loading():
    evaluator = RationEvaluator()
    assert hasattr(evaluator, "is_ready")


def test_ml_validation():
    evaluator = RationEvaluator()
    bad_data = {"calories": "none"}
    assert evaluator.validate_input(bad_data) == False

    good_data = {"calories": 2000, "protein": 100, "fat": 70, "carbs": 250}
    assert evaluator.validate_input(good_data) == True


def test_ml_prediction_format():
    evaluator = RationEvaluator()
    # Even if model is not loaded, it should return a string (error message)
    res = evaluator.predict({"calories": 2000, "protein": 100, "fat": 70, "carbs": 250})
    assert isinstance(res, str)
