#!/usr/bin/env python3
"""Start the Purple backend server.

After `pip install -e .` run `purple`, or run `python -m purple.run` from anywhere.
"""

import uvicorn

from purple.config import settings


def main() -> None:
    uvicorn.run("purple.app:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
