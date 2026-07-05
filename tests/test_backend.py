"""
Integration tests for the Doc2Draw FastAPI backend.
Exercises the full pipeline in-process via TestClient (no server needed).
"""
import io
import time
import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


SAMPLE_MD = b"""# Chapter 1: Getting Started
- Install the tool
- Configure your workspace
- Run your first scenario

# Chapter 2: Going Further
- Advanced automation patterns
- Error handling strategies
"""


class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _run_pipeline(self, filename, content, content_type):
        r = self.client.post(
            "/api/v1/projects/upload",
            files={"file": (filename, io.BytesIO(content), content_type)},
        )
        self.assertEqual(r.status_code, 200, r.text)
        pid = r.json()["project_id"]

        r = self.client.post(
            "/api/v1/projects/generate",
            json={"project_id": pid, "title": "Test Map", "columns": 2},
        )
        self.assertEqual(r.status_code, 200, r.text)
        jid = r.json()["job_id"]

        status = {}
        for _ in range(80):
            status = self.client.get(f"/api/v1/projects/{jid}/status").json()
            if status["status"] in ("done", "error"):
                break
            time.sleep(0.1)
        return pid, jid, status

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_full_generation_pipeline(self):
        pid, jid, status = self._run_pipeline("notes.md", SAMPLE_MD, "text/markdown")
        self.assertEqual(status["status"], "done", status)
        self.assertEqual(status["progress"], 100)
        self.assertTrue(status["result_available"])
        self.assertGreaterEqual(status["chapters_extracted"], 2)

        r = self.client.get(f"/api/v1/projects/{pid}/excalidraw")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["type"], "excalidraw")
        self.assertIn("elements", data)
        self.assertGreater(len(data["elements"]), 0)

    def test_unsupported_file_type_rejected(self):
        r = self.client.post(
            "/api/v1/projects/upload",
            files={"file": ("virus.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
        )
        self.assertEqual(r.status_code, 415)

    def test_unknown_job_returns_404(self):
        r = self.client.get("/api/v1/projects/job_does_not_exist/status")
        self.assertEqual(r.status_code, 404)

    def test_generate_without_upload_returns_404(self):
        r = self.client.post(
            "/api/v1/projects/generate",
            json={"project_id": "proj_missing", "columns": 3},
        )
        self.assertEqual(r.status_code, 404)

    def test_users_me_anonymous(self):
        r = self.client.get("/api/v1/users/me")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["id"], "anonymous")
        self.assertFalse(body["authenticated"])
        self.assertEqual(body["subscription_tier"], "free")

    def test_stripe_webhook_unconfigured_returns_503(self):
        r = self.client.post("/api/v1/webhooks/stripe", content=b"{}")
        self.assertEqual(r.status_code, 503)

    def test_health_reports_feature_flags(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("features", r.json())


if __name__ == "__main__":
    unittest.main()
