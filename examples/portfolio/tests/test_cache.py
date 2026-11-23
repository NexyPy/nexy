"""A case study is kept for five minutes; the list of work, whose filter is in the query, never."""


def test_a_case_study_tells_caches_to_keep_it(client):
    control = client.get("/work/tidepool").headers["cache-control"]
    assert control == "public, s-maxage=300, stale-while-revalidate=300"


def test_a_case_study_is_kept_in_memory_after_the_first_visit(client, cached):
    client.get("/work/atlas")
    assert cached("/work/atlas")


def test_an_unknown_case_study_is_not_kept(client, cached):
    client.get("/work/nothing-here")
    assert not cached("/work/nothing-here")


def test_the_work_list_is_not_kept(client, cached):
    client.get("/work?discipline=brand")
    assert not cached("/work")


def test_the_work_list_does_not_tell_caches_to_keep_it(client):
    assert "s-maxage" not in client.get("/work").headers.get("cache-control", "")
