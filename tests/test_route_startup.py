import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class StartupRouteTests(unittest.TestCase):
    def test_application_starts_with_both_user_routes(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "data"
            data.mkdir()
            (data / "sample_products.json").write_text("[]\n")
            result = subprocess.run(
                [sys.executable, "-c", """
from app import app
client = app.test_client()
assert client.get("/").status_code == 200
user = client.get("/v1/user/fixture-admin")
assert user.status_code == 200
assert user.json["username"] == "fixture-admin"
assert client.delete("/v1/user/fixture-admin").status_code == 401
"""],
                cwd=directory,
                env=dict(
                    os.environ,
                    PYTHONPATH=str(source),
                    ADMIN_USERNAME="fixture-admin",
                    ADMIN_PASSWORD="fixture-only",
                    ADMIN_EMAIL="fixture@example.invalid",
                    SECRET_KEY="fixture-only",
                ),
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
