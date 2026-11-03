"""Tugas D: test otomatis untuk health check, validasi POST, dan GET /messages/{id}.

Jalankan: python3 -m unittest -v test_app.py
Server dijalankan di thread terpisah pada port acak dengan file data sementara,
sehingga test tidak menyentuh data produksi di named volume.
"""
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

_TMP_DIR = tempfile.mkdtemp()
os.environ["DATA_FILE"] = os.path.join(_TMP_DIR, "messages.json")

import app  # noqa: E402  (DATA_FILE harus di-set sebelum import)


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.APIHandler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        app.write_messages([])

    def request(self, method, path, body=None):
        data = None if body is None else body.encode("utf-8")
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_health_returns_active(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")

    def test_post_valid_message_returns_201(self):
        status, body = self.request("POST", "/messages", '{"message": "halo"}')
        self.assertEqual(status, 201)
        self.assertEqual(body["message"]["message"], "halo")
        self.assertIn("created_at", body["message"])

    def test_post_empty_message_returns_400(self):
        status, _ = self.request("POST", "/messages", '{"message": "   "}')
        self.assertEqual(status, 400)

    def test_post_too_long_message_returns_400(self):
        status, _ = self.request("POST", "/messages",
                                 json.dumps({"message": "x" * 501}))
        self.assertEqual(status, 400)

    def test_post_invalid_json_returns_400(self):
        status, _ = self.request("POST", "/messages", "bukan json")
        self.assertEqual(status, 400)

    def test_get_message_by_id(self):
        self.request("POST", "/messages", '{"message": "pertama"}')
        status, body = self.request("GET", "/messages/0")
        self.assertEqual(status, 200)
        self.assertEqual(body["message"]["message"], "pertama")
        status, _ = self.request("GET", "/messages/99")
        self.assertEqual(status, 404)

    def test_delete_missing_index_returns_404(self):
        status, _ = self.request("DELETE", "/messages?index=999")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
