"""OPEN-192 (Phase 3, scraper-execution migration): `_upload_and_verify` gained a second
transport -- `ARCHIVE_S3_MODE=direct`, an ordinary boto3 PutObject for running this same
archive code from a cloud container that has no sudo and no wrapper binary at all, alongside
the original `ARCHIVE_S3_MODE=wrapper` (default) Mac path, unchanged.

No Django/DB fixtures needed here -- these are pure S3-transport and verification-logic tests,
deliberately kept in their own file rather than added to test_text_extract.py's Django-backed
suite, matching this directory's existing split (test_archive_concurrent_writes.py,
test_archive_per_media.py) by concern rather than by which module the code lives in.
"""

import hashlib
import os
from unittest import mock

import pytest  # type: ignore
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from openstates.cli.text_extract import (
    _check_etag,
    _upload_and_verify,
    _upload_and_verify_direct,
    S3_BILL_ARCHIVE_BUCKET,
)


def _client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "boom"}}, "PutObject")


class TestCheckEtag:
    """The verification rule both transports share -- see its own docstring for why a single
    shared function exists at all."""

    def test_matching_single_part_etag_verifies(self):
        assert _check_etag("abc123", "abc123", "some/key") is True

    def test_missing_etag_fails(self):
        assert _check_etag("", "abc123", "some/key") is False
        assert _check_etag(None, "abc123", "some/key") is False

    def test_multipart_etag_fails_even_if_it_happens_to_contain_the_hash(self):
        # A "-N" suffix means "hash of part-hashes", not a plain MD5 -- not comparable to
        # local_md5 at all, regardless of what the prefix looks like.
        assert _check_etag("abc123-2", "abc123-2", "some/key") is False

    def test_mismatched_etag_fails(self):
        assert _check_etag("abc123", "def456", "some/key") is False


class TestUploadAndVerifyDispatch:
    """`_upload_and_verify` itself does nothing but read ARCHIVE_S3_MODE and dispatch --
    verifying that dispatch is correct is independent of either transport's own internals,
    which get their own test classes below."""

    def test_default_mode_calls_wrapper_path(self, monkeypatch):
        monkeypatch.delenv("ARCHIVE_S3_MODE", raising=False)
        with mock.patch(
            "openstates.cli.text_extract._upload_and_verify_via_wrapper",
            return_value="s3://wrapper-result",
        ) as wrapper, mock.patch(
            "openstates.cli.text_extract._upload_and_verify_direct"
        ) as direct:
            result = _upload_and_verify("/tmp/x", "some/key", "abc123")
        assert result == "s3://wrapper-result"
        wrapper.assert_called_once_with("/tmp/x", "some/key", "abc123")
        direct.assert_not_called()

    def test_explicit_wrapper_mode_calls_wrapper_path(self, monkeypatch):
        monkeypatch.setenv("ARCHIVE_S3_MODE", "wrapper")
        with mock.patch(
            "openstates.cli.text_extract._upload_and_verify_via_wrapper",
            return_value="s3://wrapper-result",
        ) as wrapper:
            result = _upload_and_verify("/tmp/x", "some/key", "abc123")
        assert result == "s3://wrapper-result"
        wrapper.assert_called_once()

    def test_direct_mode_calls_direct_path(self, monkeypatch):
        monkeypatch.setenv("ARCHIVE_S3_MODE", "direct")
        with mock.patch(
            "openstates.cli.text_extract._upload_and_verify_direct",
            return_value="s3://direct-result",
        ) as direct, mock.patch(
            "openstates.cli.text_extract._upload_and_verify_via_wrapper"
        ) as wrapper:
            result = _upload_and_verify("/tmp/x", "some/key", "abc123")
        assert result == "s3://direct-result"
        direct.assert_called_once_with("/tmp/x", "some/key", "abc123")
        wrapper.assert_not_called()

    def test_unrecognized_mode_fails_closed_instead_of_falling_back_to_wrapper(
        self, monkeypatch
    ):
        # A typo'd ARCHIVE_S3_MODE (e.g. "driect") must not silently invoke the sudo-gated Mac
        # wrapper -- that binary doesn't exist in a cloud container, so falling back to it would
        # trade one clear failure for a confusing one deeper in the stack.
        monkeypatch.setenv("ARCHIVE_S3_MODE", "driect")
        with mock.patch(
            "openstates.cli.text_extract._upload_and_verify_via_wrapper"
        ) as wrapper, mock.patch(
            "openstates.cli.text_extract._upload_and_verify_direct"
        ) as direct:
            result = _upload_and_verify("/tmp/x", "some/key", "abc123")
        assert result is None
        wrapper.assert_not_called()
        direct.assert_not_called()


class TestUploadAndVerifyDirect:
    """OPEN-192's cloud transport, corrected 2026-08-31 (OPEN-238) to a single write: no more
    separate "working tier" bucket -- one `put_object` to `S3_BILL_ARCHIVE_BUCKET` at
    `GLACIER_IR` instead of `DEEP_ARCHIVE` is both the archive and the readable copy at once.
    Corrected again 2026-09-09: `STANDARD_IA` -> `GLACIER_IR`, matching the bucket-wide re-tier
    of the historical Deep Archive corpus to `GLACIER_IR` (cheaper storage for a mostly-cold
    archive outweighs its higher per-GB retrieval fee at this archive's actual read volume).
    Every test supplies its own real bytes on disk and its own real MD5 of them -- matching how
    the caller (`archive_bill_versions`) actually computes `local_md5` -- rather than asserting
    against a hand-typed hash string."""

    def _write_temp_file(self, tmp_path, content: bytes):
        path = tmp_path / "document.pdf"
        path.write_bytes(content)
        return str(path), hashlib.md5(content).hexdigest()

    def test_successful_upload_writes_glacier_ir_and_returns_uri(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        object_key = "bills/raw/fl/2026/lower/x.pdf"
        client = mock.Mock()
        client.head_object.return_value = {"ETag": f'"{md5}"'}
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, object_key, md5)

        assert result == f"s3://{S3_BILL_ARCHIVE_BUCKET}/{object_key}"
        assert client.put_object.call_count == 1  # exactly one write, not two
        put = client.put_object.call_args
        assert put.kwargs["Bucket"] == S3_BILL_ARCHIVE_BUCKET
        assert put.kwargs["Key"] == object_key
        # GLACIER_IR, not DEEP_ARCHIVE -- OPEN-238's whole point is that this single write is
        # immediately readable, no ~12h restore, in the same bucket the historical corpus
        # already lives in.
        assert put.kwargs["StorageClass"] == "GLACIER_IR"
        # The verify call has to check the same object it just wrote, not some other one --
        # a regression that verified the wrong key/bucket would otherwise still pass.
        client.head_object.assert_called_once_with(
            Bucket=S3_BILL_ARCHIVE_BUCKET, Key=object_key
        )

    def test_head_object_failure_returns_none(self, tmp_path):
        # The write can succeed while the verification call itself fails (permissions,
        # throttling, a transient network blip) -- this must return None exactly like a
        # put_object failure does, not treat "the write didn't raise" as good enough.
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.head_object.side_effect = _client_error("AccessDenied")
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_head_object_non_client_botocore_error_returns_none(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.head_object.side_effect = NoCredentialsError()
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_put_object_failure_returns_none(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.put_object.side_effect = _client_error("AccessDenied")
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_etag_mismatch_returns_none(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.head_object.return_value = {"ETag": '"not-the-real-md5"'}
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_multipart_etag_returns_none(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.head_object.return_value = {"ETag": f'"{md5}-2"'}
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_client_construction_failure_returns_none(self, tmp_path):
        # _get_s3_client() itself can raise (e.g. ProfileNotFound from a misconfigured
        # AWS_PROFILE) before any put_object/head_object call is even reachable -- this must
        # be caught too, not just failures from calls made on an already-constructed client.
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client",
            side_effect=NoCredentialsError(),
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_non_client_botocore_error_returns_none(self, tmp_path):
        # NoCredentialsError/EndpointConnectionError are BotoCoreError subclasses, not
        # ClientError -- they never got a response from S3 to wrap at all. This function's
        # contract is "None on any failure," so these must be caught too, not just ClientError.
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.put_object.side_effect = NoCredentialsError()
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_endpoint_connection_error_returns_none(self, tmp_path):
        path, md5 = self._write_temp_file(tmp_path, b"pdf bytes")
        client = mock.Mock()
        client.put_object.side_effect = EndpointConnectionError(
            endpoint_url="https://s3.amazonaws.com"
        )
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(path, "some/key", md5)
        assert result is None

    def test_unreadable_local_file_returns_none_without_attempting_a_put(self):
        # _get_s3_client() itself is just object construction (no network call), so it's fine
        # for this to run before the file read fails -- what matters is that no S3 *API call*
        # (put_object) is ever attempted for bytes that were never successfully read.
        client = mock.Mock()
        with mock.patch(
            "openstates.cli.text_extract._get_s3_client", return_value=client
        ):
            result = _upload_and_verify_direct(
                "/nonexistent/path/does/not/exist.pdf", "some/key", "abc123"
            )
        assert result is None
        client.put_object.assert_not_called()
