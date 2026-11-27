"""The trust decision the installer makes before it writes a single file."""

from __future__ import annotations

from typing import Protocol


class SignatureError(ValueError):
    """The release has no acceptable signature for this project."""


class SignatureVerifier(Protocol):
    """Check an archive signature and return the identity of its signer."""

    def verify(self, archive: bytes, signature: str | None) -> str | None: ...


def verify_signature(
    verifier: SignatureVerifier | None,
    archive: bytes,
    signature: str | None,
    required: bool,
) -> str | None:
    """Return the signer, or refuse the release under the project's trust policy."""
    if verifier is None:
        if signature is not None:
            raise SignatureError("a signed release needs a verifier")
        if required:
            raise SignatureError("this project requires signed modules")
        return None
    signer = verifier.verify(archive, signature)
    if signer is None and signature is not None:
        raise SignatureError("the release signature could not be verified")
    if signer is None and required:
        raise SignatureError("this project requires signed modules")
    return signer
