import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db
from app.utils import generate_short_string

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app, follow_redirects=False)


# ── utils ─────────────────────────────────────────────────────────────────────

def test_generate_short_string_default_length():
    sid = generate_short_string()
    assert len(sid) == 7


def test_generate_short_string_custom_length():
    sid = generate_short_string(length=10)
    assert len(sid) == 10


def test_generate_short_string_uses_allowed_chars():
    import string
    allowed = set(string.ascii_letters + string.digits)
    for _ in range(50):
        sid = generate_short_string()
        assert set(sid).issubset(allowed)


# ── POST /shorten ─────────────────────────────────────────────────────────────

def test_shorten_returns_201():
    response = client.post("/shorten", json={"url": "https://www.google.com"})
    assert response.status_code == 201


def test_shorten_returns_short_id():
    response = client.post("/shorten", json={"url": "https://www.google.com"})
    data = response.json()
    assert "short_id" in data
    assert len(data["short_id"]) == 7


def test_shorten_returns_correct_original_url():
    url = "https://github.com/DimondoAgent"
    response = client.post("/shorten", json={"url": url})
    assert response.json()["original_url"] == url


def test_shorten_returns_zero_clicks_on_create():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.json()["clicks"] == 0


def test_shorten_two_calls_produce_different_ids():
    r1 = client.post("/shorten", json={"url": "https://example.com"})
    r2 = client.post("/shorten", json={"url": "https://example.com"})
    assert r1.json()["short_id"] != r2.json()["short_id"]


def test_shorten_invalid_url_returns_422():
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422


def test_shorten_url_too_long_returns_422():
    long_url = "https://example.com/" + "a" * 2048
    response = client.post("/shorten", json={"url": long_url})
    assert response.status_code == 422


# ── GET /{short_id} ───────────────────────────────────────────────────────────

def test_redirect_returns_302():
    shorten = client.post("/shorten", json={"url": "https://openai.com"})
    short_id = shorten.json()["short_id"]
    response = client.get(f"/{short_id}")
    assert response.status_code == 302


def test_redirect_location_header_matches_original_url():
    shorten = client.post("/shorten", json={"url": "https://openai.com"})
    short_id = shorten.json()["short_id"]
    response = client.get(f"/{short_id}")
    assert response.headers["location"] in ("https://openai.com", "https://openai.com/")


def test_redirect_unknown_id_returns_404():
    response = client.get("/doesnotexist")
    assert response.status_code == 404


# ── GET /stats/{short_id} ─────────────────────────────────────────────────────

def test_stats_initial_clicks_is_zero():
    shorten = client.post("/shorten", json={"url": "https://python.org"})
    short_id = shorten.json()["short_id"]
    stats = client.get(f"/stats/{short_id}")
    assert stats.status_code == 200
    assert stats.json()["total_clicks"] == 0


def test_stats_clicks_increment_on_redirect():
    shorten = client.post("/shorten", json={"url": "https://fastapi.tiangolo.com"})
    short_id = shorten.json()["short_id"]
    client.get(f"/{short_id}")
    client.get(f"/{short_id}")
    client.get(f"/{short_id}")
    stats = client.get(f"/stats/{short_id}")
    assert stats.json()["total_clicks"] == 3


def test_stats_unknown_id_returns_404():
    response = client.get("/stats/doesnotexist")
    assert response.status_code == 404


def test_stats_response_contains_required_fields():
    shorten = client.post("/shorten", json={"url": "https://docs.python.org"})
    short_id = shorten.json()["short_id"]
    stats = client.get(f"/stats/{short_id}")
    data = stats.json()
    assert set(data.keys()) >= {"short_id", "total_clicks", "created_at"}