#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._loading._load_configs.

``load_configs`` normalises every filename stem + every nested key to
UPPER_CASE on load (introduced 2026-05). These tests exercise the
public API end-to-end against real YAML files on disk — there is no
mocking. Each test writes its own ``config_dir`` under ``tmp_path``
and passes it through the ``config_dir=`` kwarg.

Behaviours under test:

  * Filename → UPPER stem
  * Nested key → UPPER attribute
  * Multi-file merge
  * Case-conflict resolution (UPPER wins; lowercase dropped + warning)
  * DEBUG_/debug_ promotion when IS_DEBUG is set
  * Each of the three IS_DEBUG triggers (kwarg, ``CI=True``, IS_DEBUG.yaml)
  * Empty / error paths
  * ``categories/`` subdirectory
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import pytest
import yaml

from scitex_io import load_configs
from scitex_io._utils import DotDict


# ---------------------------------------------------------------------------
# Helpers — write a config_dir on disk and return its path.
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data))


def _build_config_dir(tmp_path: Path, files: dict, categories: dict | None = None) -> Path:
    """Write ``files`` (and optional ``categories``) under ``tmp_path/config``.

    ``files`` maps filename (with ``.yaml`` suffix) → data dict.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        _write_yaml(config_dir / name, data)
    if categories:
        cat_dir = config_dir / "categories"
        cat_dir.mkdir(parents=True, exist_ok=True)
        for name, data in categories.items():
            _write_yaml(cat_dir / name, data)
    return config_dir


# ---------------------------------------------------------------------------
# Filename → UPPER stem + key → UPPER attribute (basic shape).
# ---------------------------------------------------------------------------


@pytest.fixture
def basic_two_file_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "config1.yaml": {"param1": "value1", "param2": 123},
            "config2.yaml": {"param3": "value3"},
        },
    )
    return load_configs(IS_DEBUG=False, config_dir=config_dir)


def test_load_configs_basic_returns_dotdict(basic_two_file_result):
    # Arrange
    result = basic_two_file_result
    # Act
    is_dotdict = isinstance(result, DotDict)
    # Assert
    assert is_dotdict


def test_load_configs_basic_namespaces_config1_param1(basic_two_file_result):
    # Arrange
    result = basic_two_file_result
    # Act
    value = result.CONFIG1.PARAM1
    # Assert
    assert value == "value1"


def test_load_configs_basic_namespaces_config1_param2(basic_two_file_result):
    # Arrange
    result = basic_two_file_result
    # Act
    value = result.CONFIG1.PARAM2
    # Assert
    assert value == 123


def test_load_configs_basic_namespaces_config2_param3(basic_two_file_result):
    # Arrange
    result = basic_two_file_result
    # Act
    value = result.CONFIG2.PARAM3
    # Assert
    assert value == "value3"


@pytest.fixture
def already_upper_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path, {"MODEL.yaml": {"HIDDEN_DIM": 256, "DROPOUT": 0.3}}
    )
    return load_configs(IS_DEBUG=False, config_dir=config_dir)


def test_load_configs_already_upper_keeps_hidden_dim(already_upper_result):
    # Arrange
    result = already_upper_result
    # Act
    value = result.MODEL.HIDDEN_DIM
    # Assert
    assert value == 256


def test_load_configs_already_upper_keeps_dropout(already_upper_result):
    # Arrange
    result = already_upper_result
    # Act
    value = result.MODEL.DROPOUT
    # Assert
    assert value == 0.3


@pytest.fixture
def merged_three_file_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "a.yaml": {"param1": "value1", "shared": "from_a"},
            "b.yaml": {"param2": "value2", "shared": "from_b"},
            "c.yaml": {"param3": "value3"},
        },
    )
    return load_configs(IS_DEBUG=False, config_dir=config_dir)


def test_load_configs_merge_preserves_a_param1(merged_three_file_result):
    # Arrange
    result = merged_three_file_result
    # Act
    value = result.A.PARAM1
    # Assert
    assert value == "value1"


def test_load_configs_merge_preserves_a_shared(merged_three_file_result):
    # Arrange
    result = merged_three_file_result
    # Act
    value = result.A.SHARED
    # Assert
    assert value == "from_a"


def test_load_configs_merge_preserves_b_param2(merged_three_file_result):
    # Arrange
    result = merged_three_file_result
    # Act
    value = result.B.PARAM2
    # Assert
    assert value == "value2"


def test_load_configs_merge_preserves_b_shared(merged_three_file_result):
    # Arrange
    result = merged_three_file_result
    # Act
    value = result.B.SHARED
    # Assert
    assert value == "from_b"


def test_load_configs_merge_preserves_c_param3(merged_three_file_result):
    # Arrange
    result = merged_three_file_result
    # Act
    value = result.C.PARAM3
    # Assert
    assert value == "value3"


# ---------------------------------------------------------------------------
# Lowercase / nested key normalisation.
# ---------------------------------------------------------------------------


@pytest.fixture
def preprocess_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "preprocess.yaml": {
                "sample_rate": 1000,
                "bandpass_low": 0.5,
                "nested": {"field_a": "a", "field_b": 42},
            }
        },
    )
    return load_configs(IS_DEBUG=False, config_dir=config_dir)


def test_load_configs_uppercases_lowercase_sample_rate(preprocess_result):
    # Arrange
    result = preprocess_result
    # Act
    value = result.PREPROCESS.SAMPLE_RATE
    # Assert
    assert value == 1000


def test_load_configs_uppercases_lowercase_bandpass_low(preprocess_result):
    # Arrange
    result = preprocess_result
    # Act
    value = result.PREPROCESS.BANDPASS_LOW
    # Assert
    assert value == 0.5


def test_load_configs_uppercases_nested_field_a(preprocess_result):
    # Arrange
    result = preprocess_result
    # Act
    value = result.PREPROCESS.NESTED.FIELD_A
    # Assert
    assert value == "a"


def test_load_configs_uppercases_nested_field_b(preprocess_result):
    # Arrange
    result = preprocess_result
    # Act
    value = result.PREPROCESS.NESTED.FIELD_B
    # Assert
    assert value == 42


# ---------------------------------------------------------------------------
# Filename case-conflict — UPPER wins, lowercase dropped + warning.
# ---------------------------------------------------------------------------


@pytest.fixture
def filename_conflict_caught(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "MODEL.yaml": {"HIDDEN_DIM": 256},
            "model.yaml": {"SHOULD_BE_DROPPED": True},
        },
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    msgs = [str(item.message) for item in w if "case conflict" in str(item.message)]
    return result, msgs


def test_load_configs_filename_conflict_emits_warning_with_variants(
    filename_conflict_caught,
):
    # Arrange
    _result, msgs = filename_conflict_caught
    # Act
    has_variants_msg = any(
        "MODEL" in m and "model" in m for m in msgs
    )
    # Assert
    assert has_variants_msg


def test_load_configs_filename_conflict_keeps_upper_hidden_dim(
    filename_conflict_caught,
):
    # Arrange
    result, _msgs = filename_conflict_caught
    # Act
    value = result.MODEL.HIDDEN_DIM
    # Assert
    assert value == 256


def test_load_configs_filename_conflict_drops_lowercase_value(
    filename_conflict_caught,
):
    # Arrange
    result, _msgs = filename_conflict_caught
    # Act
    has_dropped_key = "SHOULD_BE_DROPPED" in result.MODEL
    # Assert
    assert has_dropped_key is False


def test_load_configs_filename_conflict_removes_lowercase_filename(
    filename_conflict_caught,
):
    # Arrange
    result, _msgs = filename_conflict_caught
    # Act
    has_lower_key = "model" in result
    # Assert
    assert has_lower_key is False


@pytest.fixture
def nested_key_conflict_caught(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "m.yaml": {
                "HIDDEN_DIM": 256,
                "hidden_dim": 999,  # collides; should be dropped
            }
        },
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    msgs = [str(item.message) for item in w if "case conflict" in str(item.message)]
    return result, msgs


def test_load_configs_nested_conflict_emits_at_least_one_warning(
    nested_key_conflict_caught,
):
    # Arrange
    _result, msgs = nested_key_conflict_caught
    # Act
    has_msg = bool(msgs)
    # Assert
    assert has_msg


def test_load_configs_nested_conflict_message_names_upper_key(
    nested_key_conflict_caught,
):
    # Arrange
    _result, msgs = nested_key_conflict_caught
    # Act
    first = msgs[0]
    # Assert
    assert "HIDDEN_DIM" in first


def test_load_configs_nested_conflict_keeps_upper_value(
    nested_key_conflict_caught,
):
    # Arrange
    result, _msgs = nested_key_conflict_caught
    # Act
    value = result.M.HIDDEN_DIM
    # Assert
    assert value == 256


# ---------------------------------------------------------------------------
# Debug promotion — DEBUG_<KEY> / debug_<KEY> override <KEY> when on.
# ---------------------------------------------------------------------------


@pytest.fixture
def debug_top_level_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "config1.yaml": {
                "param1": "normal_value",
                "DEBUG_param1": "debug_value",
                "debug_param2": "another_debug_value",
            }
        },
    )
    return load_configs(IS_DEBUG=True, config_dir=config_dir)


def test_load_configs_debug_replaces_upper_prefixed_value(debug_top_level_result):
    # Arrange
    result = debug_top_level_result
    # Act
    value = result.CONFIG1.PARAM1
    # Assert
    assert value == "debug_value"


def test_load_configs_debug_replaces_lower_prefixed_value(debug_top_level_result):
    # Arrange
    result = debug_top_level_result
    # Act
    value = result.CONFIG1.PARAM2
    # Assert
    assert value == "another_debug_value"


@pytest.fixture
def debug_nested_result(tmp_path):
    config_dir = _build_config_dir(
        tmp_path,
        {
            "config1.yaml": {
                "top_level": {
                    "normal_key": "normal_value",
                    "DEBUG_special_key": "debug_special_value",
                    "nested": {"debug_nested_key": "debug_nested_value"},
                }
            }
        },
    )
    return load_configs(IS_DEBUG=True, config_dir=config_dir)


def test_load_configs_debug_promotes_nested_special_key(debug_nested_result):
    # Arrange
    result = debug_nested_result
    # Act
    value = result.CONFIG1.TOP_LEVEL.SPECIAL_KEY
    # Assert
    assert value == "debug_special_value"


def test_load_configs_debug_promotes_doubly_nested_key(debug_nested_result):
    # Arrange
    result = debug_nested_result
    # Act
    value = result.CONFIG1.TOP_LEVEL.NESTED.NESTED_KEY
    # Assert
    assert value == "debug_nested_value"


def test_load_configs_debug_preserves_non_debug_nested_key(debug_nested_result):
    # Arrange
    result = debug_nested_result
    # Act
    value = result.CONFIG1.TOP_LEVEL.NORMAL_KEY
    # Assert
    assert value == "normal_value"


def test_load_configs_ci_env_triggers_debug(tmp_path, env_save_restore):
    # Arrange
    env_save_restore.set("CI", "True")
    config_dir = _build_config_dir(
        tmp_path,
        {"config1.yaml": {"param": "normal", "DEBUG_param": "debug"}},
    )
    # Act
    result = load_configs(IS_DEBUG=None, config_dir=config_dir)
    # Assert
    assert result.CONFIG1.PARAM == "debug"


def test_load_configs_is_debug_yaml_triggers_debug(tmp_path, env_save_restore):
    # Arrange
    env_save_restore.delete("CI")
    config_dir = _build_config_dir(
        tmp_path,
        {
            "config1.yaml": {"param": "normal", "DEBUG_param": "debug"},
            "IS_DEBUG.yaml": {"IS_DEBUG": True},
        },
    )
    # Act
    result = load_configs(IS_DEBUG=None, config_dir=config_dir)
    # Assert
    assert result.CONFIG1.PARAM == "debug"


def test_load_configs_show_prints_debug_substitution(tmp_path, capsys):
    # Arrange
    config_dir = _build_config_dir(
        tmp_path,
        {"config1.yaml": {"DEBUG_param": "debug_value"}},
    )
    load_configs(IS_DEBUG=True, show=True, config_dir=config_dir)
    # Act
    captured = capsys.readouterr()
    # Assert
    assert "DEBUG_param -> param" in captured.out


# ---------------------------------------------------------------------------
# Edge cases — empty file, missing config_dir, glob error.
# ---------------------------------------------------------------------------


def test_load_configs_empty_yaml_returns_dotdict(tmp_path):
    # Arrange
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "empty.yaml").write_text("")
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert isinstance(result, DotDict)


def test_load_configs_empty_dir_returns_empty_dotdict(tmp_path):
    # Arrange
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert len(result) == 0


def test_load_configs_missing_config_dir_returns_empty_dotdict(tmp_path):
    # Arrange
    missing = tmp_path / "no_such_config_dir"
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=missing)
    # Assert
    assert isinstance(result, DotDict)


def test_load_configs_categories_subdir_loaded(tmp_path):
    # Arrange
    config_dir = _build_config_dir(
        tmp_path,
        {"main.yaml": {"a": 1}},
        categories={"cat1.yaml": {"b": 2}},
    )
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert result.CAT1.B == 2


# ---------------------------------------------------------------------------
# Real filesystem round-trip (kept from the original test file).
# ---------------------------------------------------------------------------


@pytest.fixture
def round_trip_config_dir(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _write_yaml(
        config_dir / "config1.yaml",
        {
            "param1": "value1",
            "param2": 123,
            "nested": {"key1": "val1", "DEBUG_key2": "debug_val2"},
        },
    )
    _write_yaml(
        config_dir / "config2.yaml",
        {
            "param3": "value3",
            "DEBUG_param4": "debug_value4",
            "debug_param5": "debug_value5",
        },
    )
    _write_yaml(config_dir / "IS_DEBUG.yaml", {"IS_DEBUG": False})
    return config_dir


def test_round_trip_production_mode_preserves_config1_param1(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert result.CONFIG1.PARAM1 == "value1"


def test_round_trip_production_mode_preserves_nested_key1(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert result.CONFIG1.NESTED.KEY1 == "val1"


def test_round_trip_production_mode_skips_debug_promotion(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=False, config_dir=config_dir)
    # Assert
    assert "PARAM4" not in result.CONFIG2


def test_round_trip_debug_mode_promotes_upper_prefixed_key(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=True, config_dir=config_dir)
    # Assert
    assert result.CONFIG2.PARAM4 == "debug_value4"


def test_round_trip_debug_mode_promotes_lower_prefixed_key(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=True, config_dir=config_dir)
    # Assert
    assert result.CONFIG2.PARAM5 == "debug_value5"


def test_round_trip_debug_mode_promotes_nested_upper_prefixed_key(round_trip_config_dir):
    # Arrange
    config_dir = round_trip_config_dir
    # Act
    result = load_configs(IS_DEBUG=True, config_dir=config_dir)
    # Assert
    assert result.CONFIG1.NESTED.KEY2 == "debug_val2"


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
