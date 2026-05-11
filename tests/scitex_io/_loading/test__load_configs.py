#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._loading._load_configs.

from __future__ import annotations
`load_configs` normalises every filename stem + every nested key to
UPPER_CASE on load (introduced 2026-05). The tests below exercise:

  * Filename → UPPER stem
  * Nested key → UPPER attribute
  * Case-conflict resolution (UPPER wins, lowercase dropped + warning)
  * DEBUG_*/debug_* promotion when IS_DEBUG is set
  * Each of the three IS_DEBUG triggers (kwarg, ``CI=True``, IS_DEBUG.yaml)
  * Empty / missing / error paths
"""


import os
import tempfile
import warnings
from unittest.mock import patch

import pytest
import yaml

from scitex_io import load_configs
from scitex_io._utils import DotDict


class TestLoadConfigsBasic:
    """Top-level shape: filename → UPPER stem; keys → UPPER attribute."""

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_namespace_by_filename_upper(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/config1.yaml", "./config/config2.yaml"]
        mock_load.side_effect = [
            {"param1": "value1", "param2": 123},
            {"param3": "value3"},
        ]
        result = load_configs(IS_DEBUG=False)
        assert isinstance(result, DotDict)
        # Filename stem → UPPER; nested key → UPPER.
        assert result.CONFIG1.PARAM1 == "value1"
        assert result.CONFIG1.PARAM2 == 123
        assert result.CONFIG2.PARAM3 == "value3"

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_already_upper_keys_preserved(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/MODEL.yaml"]
        mock_load.return_value = {"HIDDEN_DIM": 256, "DROPOUT": 0.3}
        result = load_configs(IS_DEBUG=False)
        assert result.MODEL.HIDDEN_DIM == 256
        assert result.MODEL.DROPOUT == 0.3

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_merge_multiple_files(self, mock_load, mock_glob):
        mock_glob.return_value = [
            "./config/a.yaml",
            "./config/b.yaml",
            "./config/c.yaml",
        ]
        mock_load.side_effect = [
            {"param1": "value1", "shared": "from_a"},
            {"param2": "value2", "shared": "from_b"},
            {"param3": "value3"},
        ]
        result = load_configs(IS_DEBUG=False)
        assert result.A.PARAM1 == "value1"
        assert result.A.SHARED == "from_a"
        assert result.B.PARAM2 == "value2"
        assert result.B.SHARED == "from_b"
        assert result.C.PARAM3 == "value3"


class TestUpperNormalisation:
    """The new UPPER_CASE walker — adopted 2026-05."""

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_lowercase_keys_become_upper(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/preprocess.yaml"]
        mock_load.return_value = {
            "sample_rate": 1000,
            "bandpass_low": 0.5,
            "nested": {"field_a": "a", "field_b": 42},
        }
        result = load_configs(IS_DEBUG=False)
        assert result.PREPROCESS.SAMPLE_RATE == 1000
        assert result.PREPROCESS.BANDPASS_LOW == 0.5
        assert result.PREPROCESS.NESTED.FIELD_A == "a"
        assert result.PREPROCESS.NESTED.FIELD_B == 42

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_filename_case_conflict_warns_and_keeps_upper(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/MODEL.yaml", "./config/model.yaml"]
        mock_load.side_effect = [
            {"HIDDEN_DIM": 256},
            {"SHOULD_BE_DROPPED": True},
        ]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = load_configs(IS_DEBUG=False)
        msgs = [str(item.message) for item in w if "case conflict" in str(item.message)]
        assert any("['MODEL', 'model']" in m or "['model', 'MODEL']" in m for m in msgs)
        # UPPER variant wins.
        assert result.MODEL.HIDDEN_DIM == 256
        assert "SHOULD_BE_DROPPED" not in result.MODEL
        assert "model" not in result

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_nested_key_case_conflict_warns(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/m.yaml"]
        mock_load.return_value = {
            "HIDDEN_DIM": 256,
            "hidden_dim": 999,  # collides; should be dropped
        }
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = load_configs(IS_DEBUG=False)
        msgs = [str(item.message) for item in w if "case conflict" in str(item.message)]
        assert msgs, "expected a case-conflict warning"
        assert "HIDDEN_DIM" in msgs[0]
        assert result.M.HIDDEN_DIM == 256


class TestDebugPromotion:
    """DEBUG_<KEY> overrides <KEY> when IS_DEBUG is on."""

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_debug_replaces_normal_value(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {
            "param1": "normal_value",
            "DEBUG_param1": "debug_value",
            "debug_param2": "another_debug_value",
        }
        result = load_configs(IS_DEBUG=True)
        # debug promotion happens before UPPER normalisation, so the
        # stripped key gets UPPER-folded along with everything else.
        assert result.CONFIG1.PARAM1 == "debug_value"
        assert result.CONFIG1.PARAM2 == "another_debug_value"

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_debug_in_nested_dict(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {
            "top_level": {
                "normal_key": "normal_value",
                "DEBUG_special_key": "debug_special_value",
                "nested": {"debug_nested_key": "debug_nested_value"},
            }
        }
        result = load_configs(IS_DEBUG=True)
        assert result.CONFIG1.TOP_LEVEL.SPECIAL_KEY == "debug_special_value"
        assert result.CONFIG1.TOP_LEVEL.NESTED.NESTED_KEY == "debug_nested_value"
        assert result.CONFIG1.TOP_LEVEL.NORMAL_KEY == "normal_value"

    @patch("scitex_io._loading._load_configs.os.getenv")
    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_ci_env_triggers_debug(self, mock_load, mock_glob, mock_getenv):
        mock_getenv.return_value = "True"
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {"param": "normal", "DEBUG_param": "debug"}
        result = load_configs(IS_DEBUG=None)
        assert result.CONFIG1.PARAM == "debug"

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    @patch("scitex_io._loading._load_configs.os.path.exists")
    def test_is_debug_yaml_triggers_debug(self, mock_exists, mock_load, mock_glob):
        def exists_side_effect(path):
            return "IS_DEBUG.yaml" in path

        mock_exists.side_effect = exists_side_effect
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.side_effect = [
            {"IS_DEBUG": True},
            {"param": "normal", "DEBUG_param": "debug"},
        ]
        result = load_configs(IS_DEBUG=None)
        assert result.CONFIG1.PARAM == "debug"

    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_show_prints_debug_substitution(self, mock_load, mock_glob, capsys):
        mock_glob.return_value = ["./config/config1.yaml"]
        mock_load.return_value = {"DEBUG_param": "debug_value"}
        load_configs(IS_DEBUG=True, show=True)
        captured = capsys.readouterr()
        assert "DEBUG_param -> param" in captured.out


class TestEdgeCases:
    @patch("scitex_io._loading._load_configs.glob")
    @patch("scitex_io._loading._load_configs.load")
    def test_empty_file_returns_empty(self, mock_load, mock_glob):
        mock_glob.return_value = ["./config/empty.yaml"]
        mock_load.return_value = None
        result = load_configs()
        assert isinstance(result, DotDict)
        assert len(result) == 0

    @patch("scitex_io._loading._load_configs.glob")
    def test_exception_returns_empty_and_prints(self, mock_glob, capsys):
        mock_glob.side_effect = Exception("Test error")
        result = load_configs()
        assert isinstance(result, DotDict)
        assert len(result) == 0
        captured = capsys.readouterr()
        assert "Error loading configs" in captured.out


class TestRealFilesystem:
    """End-to-end with real YAML files on disk."""

    @pytest.fixture
    def temp_config_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "config")
            os.makedirs(config_dir)

            with open(os.path.join(config_dir, "config1.yaml"), "w") as f:
                yaml.dump(
                    {
                        "param1": "value1",
                        "param2": 123,
                        "nested": {
                            "key1": "val1",
                            "DEBUG_key2": "debug_val2",
                        },
                    },
                    f,
                )
            with open(os.path.join(config_dir, "config2.yaml"), "w") as f:
                yaml.dump(
                    {
                        "param3": "value3",
                        "DEBUG_param4": "debug_value4",
                        "debug_param5": "debug_value5",
                    },
                    f,
                )
            with open(os.path.join(config_dir, "IS_DEBUG.yaml"), "w") as f:
                yaml.dump({"IS_DEBUG": False}, f)
            yield tmpdir

    def test_round_trip_production_mode(self, temp_config_dir):
        original_cwd = os.getcwd()
        os.chdir(temp_config_dir)
        try:
            result = load_configs(IS_DEBUG=False)
            assert result.CONFIG1.PARAM1 == "value1"
            assert result.CONFIG1.PARAM2 == 123
            assert result.CONFIG2.PARAM3 == "value3"
            assert result.CONFIG1.NESTED.KEY1 == "val1"
            # No debug promotion in production.
            assert "PARAM4" not in result.CONFIG2
            assert "PARAM5" not in result.CONFIG2
        finally:
            os.chdir(original_cwd)

    def test_round_trip_debug_mode(self, temp_config_dir):
        original_cwd = os.getcwd()
        os.chdir(temp_config_dir)
        try:
            result = load_configs(IS_DEBUG=True)
            # DEBUG_param4 → param4 (UPPER → PARAM4)
            assert result.CONFIG2.PARAM4 == "debug_value4"
            assert result.CONFIG2.PARAM5 == "debug_value5"
            # nested DEBUG_key2 → key2 (UPPER → KEY2)
            assert result.CONFIG1.NESTED.KEY2 == "debug_val2"
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__)])
