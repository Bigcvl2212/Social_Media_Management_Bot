import os
import pytest

from app.services.instagram_private_api_service import InstagramSessionStore, InstagramPrivateAPIService, InstagramCredentials


def test_session_store_round_trip(tmp_path):
    store = InstagramSessionStore(str(tmp_path))
    assert store.load("user") is None
    store.save("user", {"a": 1})
    assert store.load("user") == {"a": 1}


def test_dry_run_post_photo(tmp_path):
    store = InstagramSessionStore(str(tmp_path))
    svc = InstagramPrivateAPIService(store, dry_run=True)
    res = svc.post_photo(image_path="./x.jpg", caption="hi")
    assert res["success"] is True
    assert res["dry_run"] is True
    assert res["action"] == "photo_upload"


def test_dry_run_post_reel(tmp_path):
    store = InstagramSessionStore(str(tmp_path))
    svc = InstagramPrivateAPIService(store, dry_run=True)
    res = svc.post_reel(video_path="./x.mp4", caption="hi")
    assert res["success"] is True
    assert res["dry_run"] is True
    assert res["action"] == "clip_upload"
