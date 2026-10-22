from nexy.modules.builder import Builder


def test_builder_thread_pool_runs() -> None:
    builder = Builder()
    result = builder.build(showlog=False)
    assert hasattr(result, "success")
    assert hasattr(result, "failed")
