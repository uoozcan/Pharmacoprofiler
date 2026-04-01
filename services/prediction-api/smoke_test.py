try:
    from app import app as default_app
except ModuleNotFoundError as exc:
    raise SystemExit(f"Missing runtime dependency for smoke test: {exc}")


def main() -> None:
    client = default_app.test_client()

    health = client.get("/api/health")
    if health.status_code not in (200, 503):
        raise SystemExit(f"Unexpected /api/health status: {health.status_code}")

    info = client.get("/api/info")
    if info.status_code not in (200, 503):
        raise SystemExit(f"Unexpected /api/info status: {info.status_code}")

    predict = client.post("/api/predict", json={"smiles": "CCO"})
    if predict.status_code not in (200, 503):
        raise SystemExit(f"Unexpected /api/predict status: {predict.status_code}")

    print("Smoke test completed")


if __name__ == "__main__":
    main()
