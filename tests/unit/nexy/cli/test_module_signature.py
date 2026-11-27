"""Signature policy: an unsigned module is allowed only when the project allows it."""

from __future__ import annotations

import pytest

from nexy.modules.cli.add.signature import SignatureError, SignatureVerifier, verify_signature


class Verifier:
    def __init__(self, signer: str | None):
        self.signer = signer

    def verify(self, archive: bytes, signature: str | None) -> str | None:
        return self.signer


def test_verify_signature_allows_an_unsigned_release():
    assert verify_signature(None, b"archive", None, False) is None


def test_verify_signature_refuses_a_signed_release_without_a_verifier():
    with pytest.raises(SignatureError, match="needs a verifier"):
        verify_signature(None, b"archive", "ed25519:abc", False)


def test_verify_signature_refuses_an_unsigned_release_when_signatures_are_required():
    with pytest.raises(SignatureError, match="requires signed"):
        verify_signature(None, b"archive", None, True)


def test_verify_signature_returns_the_identity_of_the_signer():
    verifier: SignatureVerifier = Verifier("Acme Inc")
    assert verify_signature(verifier, b"archive", "ed25519:abc", False) == "Acme Inc"


def test_verify_signature_refuses_an_invalid_signature():
    verifier: SignatureVerifier = Verifier(None)
    with pytest.raises(SignatureError, match="could not be verified"):
        verify_signature(verifier, b"archive", "ed25519:abc", False)


def test_verify_signature_refuses_an_unsigned_release_with_a_verifier_when_required():
    verifier: SignatureVerifier = Verifier(None)
    with pytest.raises(SignatureError, match="requires signed"):
        verify_signature(verifier, b"archive", None, True)
