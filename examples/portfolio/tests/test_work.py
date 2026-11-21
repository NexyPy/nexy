from src.content.work import DISCIPLINES, PROJECTS, featured, find, following, with_discipline


def test_find_returns_the_project_of_a_slug():
    assert find("tidepool").title == "Tidepool"


def test_find_returns_none_for_an_unknown_slug():
    assert find("nothing-here") is None


def test_every_slug_is_unique():
    assert len({project.slug for project in PROJECTS}) == len(PROJECTS)


def test_featured_lists_three_projects():
    assert len(featured()) == 3


def test_with_discipline_keeps_only_that_discipline():
    assert all("Research" in p.disciplines for p in with_discipline("research"))


def test_with_discipline_of_nothing_lists_every_project():
    assert with_discipline("") == PROJECTS


def test_with_an_unknown_discipline_lists_every_project():
    assert with_discipline("knitting") == PROJECTS


def test_every_discipline_has_a_project():
    assert all(with_discipline(slug) != PROJECTS for slug in DISCIPLINES)


def test_following_goes_to_the_next_project():
    assert following(PROJECTS[0]) == PROJECTS[1]


def test_following_the_last_project_goes_back_to_the_first():
    assert following(PROJECTS[-1]) == PROJECTS[0]


def test_every_project_has_three_pictures():
    assert all(len(project.pictures) == 3 for project in PROJECTS)
