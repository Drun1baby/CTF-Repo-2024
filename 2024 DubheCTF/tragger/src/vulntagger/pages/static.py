import os
import re
import stat
from pathlib import Path

import anyio
import anyio.to_thread
from fastapi import HTTPException
from nicegui import app
from starlette.datastructures import Headers
from starlette.responses import FileResponse
from starlette.types import Receive, Scope, Send

STATIC_PATH = Path(__file__).parent / ".." / "static"


class RangedFileResponse(FileResponse):
    def process_range_header(self, scope: Scope):
        headers = Headers(scope=scope)
        range_header = headers.get("range")
        if range_header is None:
            return
        # TODO: Support multiple ranges
        matched = re.match(r"^bytes=(?P<start>\d+)-(?P<end>\d+)$", range_header)
        if matched is None:
            return
        return int(matched["start"]), int(matched["end"])

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.stat_result is None:
            try:
                self.stat_result = await anyio.to_thread.run_sync(os.stat, self.path)
                self.set_stat_headers(self.stat_result)
            except FileNotFoundError as e:
                raise RuntimeError(f"File at path {self.path} does not exist.") from e
            else:
                mode = self.stat_result.st_mode
                if not stat.S_ISREG(mode):
                    raise RuntimeError(f"File at path {self.path} is not a file.")

        range_info = self.process_range_header(scope)
        random_accessible = await anyio.to_thread.run_sync(
            lambda path: os.path.isfile(path) and os.access(path, os.R_OK),
            self.path,
        )

        if random_accessible:
            self.headers.setdefault("accept-ranges", "bytes")

        if random_accessible and range_info:
            start, end = range_info
            full_length = self.stat_result.st_size
            self.headers["content-range"] = f"bytes {start}-{end}/{full_length}"
            self.headers["content-length"] = str(end - start + 1)
            self.status_code = 206
        else:
            start = 0
            end = self.stat_result.st_size

        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        if scope["method"].upper() == "HEAD":
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        elif "extensions" in scope and "http.response.pathsend" in scope["extensions"]:
            await send({"type": "http.response.pathsend", "path": str(self.path)})
        else:
            async with await anyio.open_file(self.path, mode="rb") as file:
                if range_info:
                    await file.seek(start)
                position = start
                more_body = True
                while more_body:
                    chunk = await file.read(self.chunk_size)
                    position += len(chunk)
                    if range_info and position >= end:
                        chunk = chunk[: end - position]
                        more_body = False  # If we're at the end of the range
                    elif len(chunk) < self.chunk_size:
                        more_body = False  # If we're at the end of the file
                    await send(
                        {
                            "type": "http.response.body",
                            "body": chunk,
                            "more_body": more_body,
                        }
                    )
        if self.background is not None:
            await self.background()
        return


@app.get("/static/{file_path:path}", include_in_schema=False)
async def static(file_path: str):
    # Pathlib is very secure and should prevent path traversal attacks
    static_file = STATIC_PATH / file_path

    if not static_file.exists():
        raise HTTPException(
            status_code=404, detail=f"File {static_file.name} not found."
        )

    file_stat = await anyio.to_thread.run_sync(os.stat, static_file)
    if not stat.S_ISREG(file_stat.st_mode):
        raise HTTPException(
            status_code=403, detail=f"File {static_file.name} is not a file."
        )

    return RangedFileResponse(
        static_file,
        stat_result=file_stat,
        headers={
            "cache-control": "public, max-age=3600",
        },
    )
