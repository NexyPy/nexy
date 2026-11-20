from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


# Three notes, so a new notebook shows what it does. Written out here, not imported from the
# application: a migration keeps doing what it did on the day it was written.
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        INSERT INTO "notes" ("title", "body", "pinned", "created_at", "updated_at") VALUES
    ('Welcome to Margin', 'Margin keeps your notes in SQLite and saves them while you type: there is no save button.

## Write in Markdown

- `#` starts a heading, `-` a list, `**two stars**` make **bold**
- a line of `|` makes a table
- the **Preview** tab shows the note as it reads

## Keep what matters on top

Pin a note and it stays first in the list. Search looks through every title and every body.', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Groceries', '# Saturday

- oat milk
- coffee beans, the light roast
- two lemons
- bread from the corner bakery

| Shop | Closes |
|---|---|
| Market | 13:00 |
| Bakery | 19:00 |', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Weekend ideas', 'Things to try on the next weekend project:

1. A reading list that sorts itself by length
2. A tiny weather page for the balcony plants
3. Learn to bake a proper loaf

> The best ideas are the ones written down before they leave.', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DELETE FROM "notes" WHERE "title" IN ('Welcome to Margin', 'Groceries', 'Weekend ideas');"""


MODELS_STATE = (
    "eJztl21vmzAQx78K4lUnbVXK+qS9S9pszdTA1LKt6jRZBhxiFWwKpm3U9bvPZyDmIUHtpH"
    "Rb1Xfwvzv7/DuMz/dmzAMSZds2F2QKj+YH495kOCbyoWt8a5g4SbQJBIG9SHkz6aYU7GUi"
    "xb6Q4gxHGZFSQDI/pYmgnEmV5VEEIvelI2WhlnJGr3OCBA+JmJNUGn78lDJlAbmTg5evyR"
    "WaURIFjWRpAHMrHYlForQJEx+VI8zmIZ9Hecy0c7IQc86W3pQJUEPCSIoFgeFFmkP6kF25"
    "zGpFRabapUixFhOQGc4jUVuuh7RmImQ7LjofuwiZTwDkcwZwZaqZWn0IKbyzdnYPdg/f7+"
    "8eSheV5lI5eCim1mCKQIXHds0HZccCFx6KsYYqqJDDdbgezXG6GuwyoMVWJt1mW5Hsg1sJ"
    "mq7+opYozU3BjfEdiggLxVy+7liDHpTfhmdHJ8OzLen1BqbkcgMU28IuTVZhA96ar8eDRR"
    "evS+7WfLeV/wug2wPTHV+4MHKcZddRneHWdHih8MaL0nLq2J8q9xrzo1Nn1EKdUMbIin/E"
    "iPOIYLaatw5qEfdk1KaQL5XnpT5ynNMG9dGkjfXrdDSW37gqgXSigtR/I5q1nxJggrDo8j"
    "6WFkFjshp4M7IFPShDt6uHTVVgk39sucDAYdGiPCn6tsFkOj53h9MvjaocD90xWKzGPqjU"
    "rf3W72c5iPF94p4Y8GpcOvZY4eWZCFM1o/ZzL03ICeeCI8ZvEQ5qh1qlVtQaVc+T4A+r3o"
    "x8rfq/UvWKUa3sKntowmZXtY4BBA/7V7c4DVDHwi2+zrdriq24rWCGQ1UzgAtplo3pkKTU"
    "n5srWtbS0tuvYu3z2rC+lIb1hqQZpPSElrUW8nxt1SYRN9pWa2/vEW2r9Frbtipb83yHTf"
    "UEwqX7C6S7M3jUpWDQcykYdC4FckZB2IpD9PO5Y69pm3RI+/SkvjB+GRHNOv+K/4B2D1yA"
    "0X9JaN8HWmcfDACXhL96mD38Bn7Jjms="
)
