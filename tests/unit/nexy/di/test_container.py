"""`@Injectable` classes: built by the container with their dependencies, in their scope."""

from __future__ import annotations

import pytest

from nexy.modules.di.container import Container, Injectable, Scope


@pytest.fixture(autouse=True)
def _clean_container():
    Container._instances.clear()
    Container.clear_request_scope()
    yield
    Container._instances.clear()
    Container.clear_request_scope()


@Injectable()
class Repository:
    def __init__(self) -> None:
        self.rows = ["a"]


@Injectable()
class Service:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository


@Injectable(Scope.TRANSIENT)
class Transient:
    def __init__(self) -> None:
        pass


@Injectable(Scope.REQUEST)
class PerRequest:
    def __init__(self) -> None:
        pass


@Injectable()
class Left:
    def __init__(self, right: Right) -> None:
        self.right = right


@Injectable()
class Right:
    def __init__(self, left: Left) -> None:
        self.left = left


class TestScopes:
    def test_a_singleton_is_built_once(self):
        assert Container.resolve(Repository) is Container.resolve(Repository)

    def test_a_transient_is_built_every_time(self):
        assert Container.resolve(Transient) is not Container.resolve(Transient)

    def test_a_request_scoped_class_is_shared_inside_a_request(self):
        assert Container.resolve(PerRequest) is Container.resolve(PerRequest)

    def test_a_new_request_gets_a_new_instance(self):
        first = Container.resolve(PerRequest)
        Container.clear_request_scope()
        assert Container.resolve(PerRequest) is not first


class TestDependencies:
    def test_an_injectable_parameter_is_resolved(self):
        assert Container.resolve(Service).repository is Container.resolve(Repository)

    def test_a_class_without_init_is_built_bare(self):
        @Injectable()
        class Plain:
            pass

        assert isinstance(Container.resolve(Plain), Plain)

    def test_a_parameter_with_a_default_may_be_left_out(self):
        @Injectable()
        class Tuned:
            def __init__(self, repository: Repository, retries: int = 3) -> None:
                self.repository, self.retries = repository, retries

        built = Container.resolve(Tuned)
        assert (built.repository.rows, built.retries) == (["a"], 3)

    def test_a_keyword_only_default_does_not_shift_the_dependencies(self):
        @Injectable()
        class Keyword:
            def __init__(self, repository: Repository, retries: int = 3, *, other: Service) -> None:
                self.repository, self.retries, self.other = repository, retries, other

        built = Container.resolve(Keyword)
        assert (built.retries, built.other.repository) == (3, built.repository)

    def test_a_parameter_that_is_not_injectable_and_has_no_default_is_an_error(self):
        @Injectable()
        class Broken:
            def __init__(self, name: str) -> None:
                self.name = name

        with pytest.raises(ValueError, match="not injectable"):
            Container.resolve(Broken)

    def test_variadic_parameters_are_ignored(self):
        @Injectable()
        class Open:
            def __init__(self, repository: Repository, *args: int, **kwargs: int) -> None:  # noqa: ARG002
                self.repository = repository

        assert Container.resolve(Open).repository.rows == ["a"]


class TestGuards:
    def test_building_an_injectable_by_hand_is_refused(self):
        with pytest.raises(TypeError, match="managed by Nexy"):
            Repository()

    def test_a_cycle_is_detected(self):
        with pytest.raises(RecursionError, match="Cycle"):
            Container.resolve(Left)

    def test_the_resolving_set_is_cleaned_after_a_failure(self):
        @Injectable()
        class Broken:
            def __init__(self, name: str) -> None:
                self.name = name

        with pytest.raises(ValueError):
            Container.resolve(Broken)
        assert Broken not in Container._resolving
