import asyncio

from nexy.routers.fbrouter import _make_request_handler


class TestStreamingResponse:
    """Sync components are served through a streaming (single-chunk) response."""

    def test_handler_returns_streaming_response(self):
        def Home() -> str:  # noqa: N802 - mirrors real compiled route components (PascalCase)
            return "<h1>Home</h1>"

        handler = _make_request_handler(Home)

        async def run():
            from fastapi import Request

            request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
            result = await handler(request)
            return result

        result = asyncio.run(run())
        assert "streamingresponse" in type(result).__name__.lower()

    def test_streaming_response_yields_full_body(self):
        body = "<h1>Home</h1>"

        async def run():
            from starlette.responses import StreamingResponse

            resp = StreamingResponse(iter([body.encode("utf-8")]), media_type="text/html")
            chunks = []
            async for chunk in resp.body_iterator:
                chunks.append(chunk)
            return b"".join(chunks)

        out = asyncio.run(run())
        assert out == body.encode()

    def test_sync_component_body_unchanged(self):
        def Home() -> str:  # noqa: N802 - mirrors real compiled route components (PascalCase)
            return "<h1>Home</h1>"

        handler = _make_request_handler(Home)

        async def run():
            from fastapi import Request

            request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
            resp = await handler(request)
            chunks = [c async for c in resp.body_iterator]
            return b"".join(chunks)

        out = asyncio.run(run())
        assert out == b"<h1>Home</h1>"

    def test_generator_component_streams_multiple_chunks(self):
        def Home():  # noqa: N802 - mirrors real compiled route components (PascalCase)
            yield "<h1>"
            yield "Home"
            yield "</h1>"

        handler = _make_request_handler(Home)

        async def run():
            from fastapi import Request

            request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
            resp = await handler(request)
            return [c async for c in resp.body_iterator]

        chunks = asyncio.run(run())
        assert len(chunks) >= 2
        assert b"".join(chunks) == b"<h1>Home</h1>"
