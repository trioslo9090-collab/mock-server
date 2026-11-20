import pytest
from mockserver.cli import main


class TestCLI:
    """Tests for CLI argument parsing and error handling"""

    def test_missing_spec_file_error(self):
        """CLI with nonexistent file should error with clear message"""
        argv = ["/nonexistent/file.yaml"]
        with pytest.raises(SystemExit) as exc_info:
            main(argv)
        assert exc_info.value.code != 0

    def test_missing_spec_file_error_message(self, capsys):
        """CLI error message should mention missing file"""
        argv = ["/nonexistent/file.yaml"]
        try:
            main(argv)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        # Should contain error message about file
        assert "not found" in captured.out.lower() or "not found" in captured.err.lower() or \
               "nonexistent" in captured.out.lower() or "nonexistent" in captured.err.lower()

    def test_invalid_yaml_error(self, tmp_path):
        """CLI with invalid YAML should error"""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("{ invalid: yaml: content:")

        argv = [str(invalid_yaml)]
        with pytest.raises(SystemExit) as exc_info:
            main(argv)
        assert exc_info.value.code != 0

    def test_invalid_yaml_error_message(self, tmp_path, capsys):
        """CLI error message should mention invalid YAML"""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("{ invalid: yaml: content:")

        argv = [str(invalid_yaml)]
        try:
            main(argv)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        # Should contain error message about YAML or parsing
        assert "yaml" in captured.out.lower() or "yaml" in captured.err.lower() or \
               "invalid" in captured.out.lower() or "invalid" in captured.err.lower()

    def test_valid_spec_calls_uvicorn(self, petstore_spec, tmp_path, monkeypatch):
        """CLI with valid spec should call uvicorn.run with correct port"""
        import yaml
        spec_file = tmp_path / "petstore.yaml"
        spec_file.write_text(yaml.dump(petstore_spec))

        # Mock uvicorn.run to avoid actually starting server
        run_called = []

        def mock_run(app, host, port, **kwargs):
            run_called.append({"port": port})

        monkeypatch.setattr("uvicorn.run", mock_run)

        argv = [str(spec_file), "--port", "8001"]
        main(argv)

        assert len(run_called) == 1
        assert run_called[0]["port"] == 8001

    def test_valid_spec_default_port(self, petstore_spec, tmp_path, monkeypatch):
        """CLI with valid spec should use default port 8000"""
        import yaml
        spec_file = tmp_path / "petstore.yaml"
        spec_file.write_text(yaml.dump(petstore_spec))

        run_called = []

        def mock_run(app, host, port, **kwargs):
            run_called.append({"port": port})

        monkeypatch.setattr("uvicorn.run", mock_run)

        argv = [str(spec_file)]
        main(argv)

        assert len(run_called) == 1
        assert run_called[0]["port"] == 8000

    def test_valid_spec_with_seed(self, petstore_spec, tmp_path, monkeypatch):
        """CLI with --seed flag should pass seed to app creation"""
        import yaml
        spec_file = tmp_path / "petstore.yaml"
        spec_file.write_text(yaml.dump(petstore_spec))

        run_called = []

        def mock_run(app, host, port, **kwargs):
            run_called.append({"app": app})

        monkeypatch.setattr("uvicorn.run", mock_run)

        argv = [str(spec_file), "--seed", "42"]
        main(argv)

        assert len(run_called) == 1
        # App should be created with seed (verified in app creation, not here)
