from src.accounts import throttle

EMAIL = "ada@example.com"


def fail(times, at=0.0):
    for _ in range(times):
        throttle.failed(EMAIL, now=at)


def test_a_few_failures_do_not_block():
    fail(throttle.LIMIT - 1)
    assert not throttle.blocked(EMAIL, now=1.0)


def test_too_many_failures_block_the_email():
    fail(throttle.LIMIT)
    assert throttle.blocked(EMAIL, now=1.0)


def test_a_block_ends_after_the_window():
    fail(throttle.LIMIT)
    assert not throttle.blocked(EMAIL, now=throttle.WINDOW + 1)


def test_a_block_is_for_one_email_only():
    fail(throttle.LIMIT)
    assert not throttle.blocked("someone@example.com", now=1.0)


def test_a_success_forgets_the_failures():
    fail(throttle.LIMIT - 1)
    throttle.succeeded(EMAIL)
    fail(1, at=2.0)
    assert not throttle.blocked(EMAIL, now=3.0)
