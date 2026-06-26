import * as vscode from "vscode";
import * as cp from "child_process";
import { extractHeader } from "../../shared/parser/header";

const FORMAT_TIMEOUT = 10_000;

export function registerFormattingProvider(context: vscode.ExtensionContext) {
  const selector = [{ language: "nexy", scheme: "file" }, { language: "mdx", scheme: "file" }];

  context.subscriptions.push(
    vscode.languages.registerDocumentFormattingEditProvider(selector, {
      async provideDocumentFormattingEdits(
        document: vscode.TextDocument,
      ): Promise<vscode.TextEdit[]> {
        const edits: vscode.TextEdit[] = [];
        const fullText = document.getText();

        const header = extractHeader(fullText);
        if (header !== null) {
          const formatted = await runRuff(header);
          if (formatted !== null && formatted !== header) {
            const headerStart = fullText.indexOf(header);
            const range = new vscode.Range(
              document.positionAt(headerStart),
              document.positionAt(headerStart + header.length),
            );
            edits.push(new vscode.TextEdit(range, formatted));
          }
        }

        const template = extractTemplatePart(fullText);
        if (template) {
          const formatted = await runPrettier(template, document.uri);
          if (formatted !== null && formatted !== template) {
            const tplStart = fullText.indexOf(template);
            const range = new vscode.Range(
              document.positionAt(tplStart),
              document.positionAt(tplStart + template.length),
            );
            edits.push(new vscode.TextEdit(range, formatted));
          }
        }

        return edits;
      },
    }),
  );
}

async function runRuff(code: string): Promise<string | null> {
  try {
    const result = await execAsync("ruff", ["format", "--stdin-filename", "header.py", "--quiet"], code, FORMAT_TIMEOUT);
    return result;
  } catch {
    return null;
  }
}

async function runPrettier(code: string, uri: vscode.Uri): Promise<string | null> {
  try {
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
    const cwd = workspaceFolder?.uri.fsPath ?? process.cwd();
    const result = await execAsync("npx", ["prettier", "--parser", "html", "--stdin-filepath", "template.html"], code, FORMAT_TIMEOUT, cwd);
    return result;
  } catch {
    return null;
  }
}

function execAsync(
  cmd: string,
  args: string[],
  stdin: string,
  timeout: number,
  cwd?: string,
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = cp.execFile(cmd, args, { cwd, timeout, maxBuffer: 1024 * 1024 }, (err, stdout) => {
      if (err) {
        reject(err);
      } else {
        resolve(stdout);
      }
    });
    if (child.stdin) {
      child.stdin.end(stdin);
    }
  });
}

function extractTemplatePart(text: string): string {
  const m = text.match(/^[ \t]*---[ \t]*\r?\n[\s\S]*?\r?\n[ \t]*---[ \t]*(?:\r?\n|$)(?<template>[\s\S]*)/);
  return m?.groups?.template ?? "";
}
