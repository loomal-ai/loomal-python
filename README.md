# Loomal Python SDK

The official Python SDK for the [Loomal API](https://loomal.ai) -- identity infrastructure for AI agents.

[![PyPI version](https://img.shields.io/pypi/v/loomal-sdk.svg)](https://pypi.org/project/loomal-sdk/)
[![Python 3.9+](https://img.shields.io/pypi/pyversions/loomal-sdk.svg)](https://pypi.org/project/loomal-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install loomal-sdk
```

> The distribution is `loomal-sdk` on PyPI, but the import name is `loomal`.

## Quick start

```python
from loomal import Loomal

client = Loomal(api_key="loid-...")

me = client.identity.whoami()
print(me.email)

client.mail.send(
    to=["colleague@example.com"],
    subject="Hello from my agent",
    text="Sent via the Loomal Python SDK.",
)
```

## Async usage

```python
from loomal import AsyncLoomal

async with AsyncLoomal(api_key="loid-...") as client:
    me = await client.identity.whoami()
    await client.mail.send(
        to=["colleague@example.com"],
        subject="Hello",
        text="Sent asynchronously.",
    )
```

## Authentication

Pass your API key directly, or set the `LOOMAL_API_KEY` environment variable:

```python
# Explicit
client = Loomal(api_key="loid-...")

# From environment
import os
os.environ["LOOMAL_API_KEY"] = "loid-..."
client = Loomal()
```

Both `Loomal` and `AsyncLoomal` support context managers for automatic resource cleanup:

```python
with Loomal() as client:
    me = client.identity.whoami()
```

## Usage

### Identity

```python
me = client.identity.whoami()
print(me.email, me.display_name)
```

### More resources

The SDK also exposes `client.mail`, `client.calendar`, `client.vault`, `client.logs`, and `client.did`. See the full reference at **[docs.loomal.ai](https://docs.loomal.ai)** for request/response shapes, pagination, and end-to-end examples.

## Error handling

All API errors raise `LoomalError` with structured fields:

```python
from loomal import LoomalError

try:
    client.mail.send(to=["a@b.com"], subject="Hi", text="Hello")
except LoomalError as e:
    print(e.status)   # HTTP status code
    print(e.code)     # Error code string
    print(e.message)  # Human-readable message
```

## Types

The SDK returns typed dataclasses, not raw dictionaries. API responses are automatically converted from camelCase to snake_case.

| Type | Description |
|------|-------------|
| `IdentityResponse` | Agent identity details |
| `MessageResponse` | Email message |
| `ThreadResponse` | Thread summary |
| `ThreadDetailResponse` | Thread with messages |
| `CredentialMetadata` | Vault credential metadata |
| `CredentialWithData` | Credential with decrypted data |
| `ActivityLog` | Single activity log entry |
| `LogsStats` | Aggregated log statistics |
| `TotpResponse` | Generated TOTP code |
| `DidDocument` | DID document |

> **Note:** The `from` field in message responses is exposed as `from_addrs` since `from` is a reserved keyword in Python.

## Requirements

- Python 3.9+
- [`httpx`](https://www.python-httpx.org/) (installed automatically)

## Links

- [Documentation](https://docs.loomal.ai)
- [Console](https://console.loomal.ai)
- [Website](https://loomal.ai)
- [PyPI](https://pypi.org/project/loomal-sdk/)

## License

MIT
