import json

import httpx
import respx
from loomal import Loomal


_STORED = {
    "credentialId": "cred-1",
    "name": "test",
    "type": "API_KEY",
    "metadata": None,
    "expiresAt": None,
    "lastUsedAt": None,
    "lastRotatedAt": None,
    "createdAt": "2026-04-16T00:00:00Z",
}


def _body(route) -> dict:
    return json.loads(route.calls.last.request.content)


class TestVaultStoreHelpers:
    @respx.mock
    def test_store_api_key_string(self):
        route = respx.put("https://api.loomal.ai/v0/vault/stripe").mock(
            return_value=httpx.Response(200, json=_STORED)
        )
        client = Loomal(api_key="loid-test")
        client.vault.store_api_key("stripe", "sk_live_abc123")
        body = _body(route)
        assert body["type"] == "API_KEY"
        assert body["data"] == {"key": "sk_live_abc123"}
        assert "clientId" not in (body.get("metadata") or {})
        client.close()

    @respx.mock
    def test_store_api_key_client_pair(self):
        route = respx.put("https://api.loomal.ai/v0/vault/twitter").mock(
            return_value=httpx.Response(200, json=_STORED)
        )
        client = Loomal(api_key="loid-test")
        client.vault.store_api_key("twitter", {"clientId": "abc123", "secret": "def456"})
        body = _body(route)
        assert body["type"] == "API_KEY"
        assert body["data"] == {"clientId": "abc123", "secret": "def456"}
        assert body["metadata"]["clientId"] == "abc123"
        client.close()

    @respx.mock
    def test_store_card(self):
        route = respx.put("https://api.loomal.ai/v0/vault/personal-visa").mock(
            return_value=httpx.Response(200, json={**_STORED, "type": "CARD"})
        )
        client = Loomal(api_key="loid-test")
        client.vault.store_card("personal-visa", {
            "cardholder": "Jane Doe",
            "number": "4242 4242 4242 4242",
            "expMonth": "12",
            "expYear": "2029",
            "cvc": "123",
            "zip": "94103",
        }, metadata={"brand": "Visa"})
        body = _body(route)
        assert body["type"] == "CARD"
        assert body["data"]["cardholder"] == "Jane Doe"
        assert body["data"]["cvc"] == "123"
        assert body["metadata"]["last4"] == "4242"
        assert body["metadata"]["brand"] == "Visa"
        client.close()

    @respx.mock
    def test_store_shipping_address(self):
        route = respx.put("https://api.loomal.ai/v0/vault/home").mock(
            return_value=httpx.Response(200, json={**_STORED, "type": "SHIPPING_ADDRESS"})
        )
        client = Loomal(api_key="loid-test")
        client.vault.store_shipping_address("home", {
            "name": "Autonomous Agent",
            "line1": "1 Demo Way",
            "city": "San Francisco",
            "state": "CA",
            "postcode": "94103",
            "country": "US",
            "phone": "+1-555-0100",
        })
        body = _body(route)
        assert body["type"] == "SHIPPING_ADDRESS"
        assert body["data"]["line1"] == "1 Demo Way"
        assert body["data"]["country"] == "US"
        assert body["data"]["phone"] == "+1-555-0100"
        client.close()

    @respx.mock
    def test_generic_store_still_works(self):
        route = respx.put("https://api.loomal.ai/v0/vault/db").mock(
            return_value=httpx.Response(200, json={**_STORED, "type": "DATABASE"})
        )
        client = Loomal(api_key="loid-test")
        client.vault.store("db", "DATABASE", {"password": "s3cr3t"}, metadata={"host": "db.example.com"})
        body = _body(route)
        assert body["type"] == "DATABASE"
        assert body["data"]["password"] == "s3cr3t"
        client.close()
