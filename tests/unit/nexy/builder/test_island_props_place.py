"""The island props stay out of the folder the client build empties before it reads them."""

from nexy.modules.builder.island_props import MANIFEST


def test_the_island_props_are_not_in_the_client_output_folder():
    assert "client" not in MANIFEST.parts
