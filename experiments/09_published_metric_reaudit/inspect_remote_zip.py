from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import urllib.request
import zipfile


class HTTPRangeReader(io.RawIOBase):
    """Minimal seekable HTTP reader for public range-enabled artifacts."""

    def __init__(self, url: str):
        self.url = url
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request) as response:
            self.length = int(response.headers["Content-Length"])
            self.etag = response.headers.get("ETag", "")
        self.position = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            position = offset
        elif whence == io.SEEK_CUR:
            position = self.position + offset
        elif whence == io.SEEK_END:
            position = self.length + offset
        else:
            raise ValueError(f"unsupported whence: {whence}")
        if position < 0:
            raise ValueError("negative seek position")
        self.position = min(position, self.length)
        return self.position

    def read(self, size: int = -1) -> bytes:
        if self.position >= self.length:
            return b""
        if size is None or size < 0:
            size = self.length - self.position
        end = min(self.position + size, self.length) - 1
        request = urllib.request.Request(
            self.url,
            headers={"Range": f"bytes={self.position}-{end}"},
        )
        with urllib.request.urlopen(request) as response:
            data = response.read()
        self.position += len(data)
        return data

    def readinto(self, buffer: bytearray) -> int:
        data = self.read(len(buffer))
        buffer[: len(data)] = data
        return len(data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List or selectively extract files from a public remote ZIP."
    )
    parser.add_argument("url")
    parser.add_argument(
        "--match",
        default=r"(?i)(config|score|metadata|stat|result|readme|\.csv$|\.json$)",
        help="Regular expression used to select member names.",
    )
    parser.add_argument("--extract-dir", type=Path)
    args = parser.parse_args()

    reader = HTTPRangeReader(args.url)
    pattern = re.compile(args.match)
    with zipfile.ZipFile(reader) as archive:
        selected = [info for info in archive.infolist() if pattern.search(info.filename)]
        print(
            f"content_length={reader.length} etag={reader.etag} "
            f"members={len(archive.infolist())} selected={len(selected)}"
        )
        for info in selected:
            print(f"{info.file_size:>12} {info.compress_size:>12} {info.filename}")
            if args.extract_dir and not info.is_dir():
                destination = args.extract_dir / info.filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
