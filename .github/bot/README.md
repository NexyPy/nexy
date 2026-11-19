# The Nexy bot

Comments and assignments made by the workflows of this repository come from **nexy**, a
GitHub App, instead of `github-actions`. `nexy.png` is its picture and `nexy.svg` the source of it.

A workflow that speaks for the project asks for a token of the app in its first step:

```yaml
- name: Act as the Nexy bot
  id: bot
  if: ${{ vars.NEXY_BOT_CLIENT_ID != '' }}
  uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3.3.0
  with:
    client-id: ${{ vars.NEXY_BOT_CLIENT_ID }}
    private-key: ${{ secrets.NEXY_BOT_PRIVATE_KEY }}
    permission-issues: write
```

and uses `${{ steps.bot.outputs.token || github.token }}`: until the app is set up, the workflow
token answers, so nothing breaks. The token gets the permissions the workflow declares, no more.

## Set it up (maintainer, once)

1. Create the app in the organization: Settings, Developer settings, GitHub Apps, New GitHub App.
   - Name: `nexy`. Homepage: `https://github.com/NexyPy/nexy`. Webhook: off.
   - Repository permissions: Issues read and write, Pull requests read and write, Metadata read.
   - Where can it be installed: only on this account.
2. On the page of the app, upload `nexy.png` as its logo and set the badge color to `#0A0A0B`.
3. Generate a private key, then install the app on `NexyPy/nexy` only.
4. In the repository, Settings, Secrets and variables, Actions:
   - variable `NEXY_BOT_CLIENT_ID`: the Client ID of the app;
   - secret `NEXY_BOT_PRIVATE_KEY`: the whole `.pem` file.

The next comment of a workflow is signed `nexy[bot]`, with the mascot.
