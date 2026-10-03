"""User 3's frozen check interface.

The static and numerical checker is under construction. This explicit failure
prevents an unfinished checker from being mistaken for successful validation.
"""


def run_checks(spec: dict, html: str) -> dict:
    return {
        "ok": False,
        "degraded": True,
        "checks": [
            {
                "id": "stub",
                "status": "skip",
                "detail": "checks not implemented",
                "target": None,
            }
        ],
        "failures": ["checks not implemented"],
        "revisions": [],
    }

