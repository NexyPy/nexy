"""The case studies of the portfolio. Noor, her clients and their numbers are made up."""

from dataclasses import dataclass

# The filter of /work: the word in the address, then the word on the page.
DISCIPLINES = {
    "product": "Product design",
    "systems": "Design systems",
    "research": "Research",
    "brand": "Brand",
}


@dataclass(frozen=True)
class Picture:
    file: str
    caption: str


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    client: str
    year: int
    disciplines: tuple[str, ...]
    summary: str
    role: str
    team: str
    duration: str
    challenge: str
    approach: tuple[str, ...]
    outcome: str
    results: tuple[tuple[str, str], ...]
    pictures: tuple[Picture, ...]
    featured: bool = False

    @property
    def cover(self) -> str:
        return f"/work/{self.slug}/cover.svg"


def _pictures(slug: str, *captions: str) -> tuple[Picture, ...]:
    return tuple(Picture(f"/work/{slug}/{n}.svg", text) for n, text in enumerate(captions, 1))


PROJECTS: list[Project] = [
    Project(
        slug="tidepool",
        title="Tidepool",
        client="Tidepool, a bank for freelancers",
        year=2026,
        disciplines=("Product design", "Research"),
        summary="Getting paid as a freelancer, from the first invoice to the tax set aside.",
        role="Lead product designer",
        team="2 designers, 6 engineers, 1 researcher",
        duration="9 months",
        challenge=(
            "Freelancers opened Tidepool to send an invoice, then left for a spreadsheet to know "
            "how much of it was theirs to spend. The app knew every payment but told them nothing "
            "about tax, late clients or the month ahead."
        ),
        approach=(
            "Sat with 14 freelancers while they did their books, and noted every question.",
            "Turned the home screen into one answer: what you can spend today, after tax.",
            "Made an invoice two fields and a client, with the rest filled from the last one.",
            "Tested every flow on a phone, outdoors, with one hand.",
        ),
        outcome=(
            "The new home shipped to every account in March. Freelancers now set tax aside "
            "automatically, and chasing a late invoice is one tap from the payment it is about."
        ),
        results=(
            ("2.1x", "faster to send an invoice, in usability tests"),
            ("61%", "of accounts set tax aside in the first month"),
            ("-38%", "support questions about tax"),
        ),
        pictures=_pictures(
            "tidepool",
            "The home screen answers one question: what is mine to spend.",
            "An invoice in two fields, filled from the last one.",
            "Tax set aside as money arrives, never as a surprise in April.",
        ),
        featured=True,
    ),
    Project(
        slug="grove",
        title="Grove",
        client="Grove Market, 140 grocery stores",
        year=2025,
        disciplines=("Design systems",),
        summary="One design system for the shelf labels, the app and the self-checkout.",
        role="Design systems lead",
        team="3 designers, 4 engineers",
        duration="1 year",
        challenge=(
            "Grove had three teams drawing the same price three ways: on the shelf label, in the "
            "app and at the self-checkout. Customers noticed when the three did not agree."
        ),
        approach=(
            "Collected every price, badge and promotion in use: 212 variants of one idea.",
            "Wrote the rules of a price once, as tokens that print, render and speak.",
            "Shipped the components to the three teams with their tests, not as a picture.",
        ),
        outcome=(
            "The shelf, the app and the checkout now draw a price from the same tokens, and a "
            "promotion is designed once instead of three times."
        ),
        results=(
            ("212 to 9", "price and promotion variants"),
            ("3", "teams on one set of components"),
            ("4 days", "to launch a promotion, down from three weeks"),
        ),
        pictures=_pictures(
            "grove",
            "The price component, from shelf label to screen reader.",
            "Tokens that print on paper and render on glass.",
            "The self-checkout, built from the same parts as the app.",
        ),
        featured=True,
    ),
    Project(
        slug="halden",
        title="Halden Rail",
        client="Halden Rail, a regional train line",
        year=2025,
        disciplines=("Research", "Product design"),
        summary="A ticket machine that a tourist and a commuter both finish in under a minute.",
        role="Researcher and interaction designer",
        team="1 designer, 1 researcher, the vendor's engineers",
        duration="5 months",
        challenge=(
            "Queues at the ticket machines made people miss trains. The machine asked eleven "
            "questions before it showed a price, in the same order for everyone."
        ),
        approach=(
            "Filmed 300 purchases, with permission, at four stations.",
            "Started from the destination: most people know where they go, not which fare.",
            "Put the three most bought tickets of each station on the first screen.",
        ),
        outcome=(
            "The new flow runs on 48 machines. The common ticket is two taps; the rare ones are "
            "still there, one screen further."
        ),
        results=(
            ("52 s", "median purchase, down from 2 min 10 s"),
            ("2 taps", "for the ticket most people buy"),
            ("48", "machines updated without new hardware"),
        ),
        pictures=_pictures(
            "halden",
            "The first screen: where to, and the tickets this station sells most.",
            "Prices before questions.",
            "Tested at the station, with the queue behind.",
        ),
        featured=True,
    ),
    Project(
        slug="ember",
        title="Ember Studio",
        client="Ember, a ceramics studio",
        year=2024,
        disciplines=("Brand",),
        summary="A mark, a palette and a shop for a studio that fires every piece by hand.",
        role="Brand and web designer",
        team="Just me, and the two potters",
        duration="10 weeks",
        challenge=(
            "Ember sold out every market but had no name online: the shop was a list of photos "
            "taken on a kitchen table."
        ),
        approach=(
            "Drew the mark from the kiln's spy hole, the only round thing in the studio.",
            "Took the palette from the glazes, so the site looks like the shelves.",
            "Built a shop with one product per page, and the story of the firing next to it.",
        ),
        outcome="The shop opened with the autumn firing and sold the batch in four days.",
        results=(
            ("4 days", "to sell the first online batch"),
            ("1", "mark, cut in rubber for the boxes"),
            ("6", "glaze colours, used as the palette"),
        ),
        pictures=_pictures(
            "ember",
            "The mark, from the kiln's spy hole.",
            "The palette, taken from the glazes.",
            "One piece per page, with its firing.",
        ),
    ),
    Project(
        slug="lumen",
        title="Lumen Health",
        client="Lumen, a network of clinics",
        year=2024,
        disciplines=("Product design", "Research"),
        summary="Test results a patient understands before the doctor calls.",
        role="Senior product designer",
        team="2 designers, 1 doctor, 5 engineers",
        duration="7 months",
        challenge=(
            "Patients got their results as a table of numbers and a reference range, then "
            "searched the web and called the clinic worried."
        ),
        approach=(
            "Wrote every result as a sentence first, with a doctor, then designed around it.",
            "Showed the range as a bar with the patient's value on it, not two numbers.",
            "Added what happens next, so a result never ends on a number.",
        ),
        outcome="Results now read as sentences, and the clinic's phone rings less after they go out.",
        results=(
            ("-27%", "calls to the clinic after results"),
            ("94%", "of patients understood their result in tests"),
            ("40", "results rewritten with a doctor"),
        ),
        pictures=_pictures(
            "lumen",
            "A result as a sentence, then the number.",
            "The range as a bar, the value on it.",
            "What happens next, on every result.",
        ),
    ),
    Project(
        slug="atlas",
        title="Atlas Trails",
        client="Atlas, offline maps for hikers",
        year=2023,
        disciplines=("Product design",),
        summary="A trail map that still works with no signal, gloves on, in the rain.",
        role="Product designer",
        team="1 designer, 3 engineers",
        duration="4 months",
        challenge=(
            "Hikers downloaded maps at home, then could not find them on the trail. The map was "
            "built for a desk, not for a cold hand on a wet screen."
        ),
        approach=(
            "Walked three trails with the team and the app, and wrote down every fumble.",
            "Made every control twice the usual size, and the map the whole screen.",
            "Downloaded the trail ahead automatically while there was still signal.",
        ),
        outcome="The trail ahead is now always on the phone, and the controls work through gloves.",
        results=(
            ("2x", "larger controls, usable with gloves"),
            ("0", "taps to save the trail ahead"),
            ("4.8", "rating after the update, from 3.9"),
        ),
        pictures=_pictures(
            "atlas",
            "The map is the screen; the controls are thumbs.",
            "The trail ahead, saved before the signal goes.",
            "Readable in direct sun and at night.",
        ),
    ),
]


def find(slug: str) -> Project | None:
    return next((project for project in PROJECTS if project.slug == slug), None)


def featured() -> list[Project]:
    return [project for project in PROJECTS if project.featured]


def with_discipline(slug: str) -> list[Project]:
    """The projects of a discipline; an empty or unknown one lists them all."""
    name = DISCIPLINES.get(slug)
    if name is None:
        return PROJECTS
    return [project for project in PROJECTS if name in project.disciplines]


def following(project: Project) -> Project:
    return PROJECTS[(PROJECTS.index(project) + 1) % len(PROJECTS)]
