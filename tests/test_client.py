import os
import pytest
from loomal import Loomal, AsyncLoomal
from loomal._errors import LoomalError


class TestLoomalClient:
    def test_requires_api_key(self):
        os.environ.pop("LOOMAL_API_KEY", None)
        with pytest.raises(ValueError, match="API key is required"):
            Loomal()

    def test_creates_with_api_key(self):
        client = Loomal(api_key="loid-test123")
        assert client.identity is not None
        assert client.mail is not None
        assert client.vault is not None
        assert client.logs is not None
        assert client.did is not None
        client.close()

    def test_reads_env_var(self):
        os.environ["LOOMAL_API_KEY"] = "loid-fromenv"
        try:
            client = Loomal()
            assert client.identity is not None
            client.close()
        finally:
            del os.environ["LOOMAL_API_KEY"]

    def test_context_manager(self):
        with Loomal(api_key="loid-test") as client:
            assert client.identity is not None


class TestAsyncLoomalClient:
    def test_requires_api_key(self):
        os.environ.pop("LOOMAL_API_KEY", None)
        with pytest.raises(ValueError, match="API key is required"):
            AsyncLoomal()


class TestLoomalError:
    def test_attributes(self):
        err = LoomalError(401, "unauthorized", "Invalid API key")
        assert err.status == 401
        assert err.code == "unauthorized"
        assert str(err) == "Invalid API key"

    def test_repr(self):
        err = LoomalError(404, "not_found", "Not found")
        assert "404" in repr(err)
