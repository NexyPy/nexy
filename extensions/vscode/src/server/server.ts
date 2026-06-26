import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  TextDocumentSyncKind,
  InitializeParams,
  InitializeResult,
  SemanticTokensLegend,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import { getLanguageService } from "vscode-html-languageservice";
import { CompletionHandler } from "./handlers/completion";
import { HoverHandler } from "./handlers/hover";
import { DiagnosticHandler } from "./handlers/diagnostics";
import { CodeActionHandler } from "./handlers/code.actions";
import { DefinitionHandler } from "./handlers/definition";
import { FoldHandler } from "./handlers/fold";
import { RenameHandler } from "./handlers/rename";
import { ReferenceHandler } from "./handlers/references";
import { getSemanticLegend, computeSemanticTokens } from "./features/semanticTokens";
import { CodeLensHandler } from "./handlers/code.lens";
import { ProjectIndexer } from "./indexer";

class NexyLspServer {
  private connection = createConnection(ProposedFeatures.all);
  private documents = new TextDocuments(TextDocument);
  private htmlLanguageService = getLanguageService();
  private indexer = new ProjectIndexer();
  
  private completionHandler = new CompletionHandler(this.htmlLanguageService);
  private hoverHandler = new HoverHandler();
  private diagnosticHandler = new DiagnosticHandler();
  private codeActionHandler = new CodeActionHandler();
  private definitionHandler = new DefinitionHandler();
  private foldHandler = new FoldHandler();
  private renameHandler = new RenameHandler(this.indexer);
  private referenceHandler = new ReferenceHandler(this.indexer);
  private codeLensHandler = new CodeLensHandler();

  constructor() {
    this.setupHandlers();
    this.documents.listen(this.connection);
    this.connection.listen();
  }

  private setupHandlers() {
    this.connection.onInitialize((params: InitializeParams): InitializeResult => {
      if (params.rootUri) this.indexer.initialize(params.rootUri);
      return {
        capabilities: {
          textDocumentSync: TextDocumentSyncKind.Incremental,
          completionProvider: {
            resolveProvider: false,
            triggerCharacters: ["<", "/", ".", ":", "{", "%", "#", "|", " ", "\"", "'", "=", "@"],
          },
          hoverProvider: true,
          codeActionProvider: true,
          definitionProvider: true,
          referencesProvider: true,
          renameProvider: { prepareProvider: true },
          foldingRangeProvider: true,
          codeLensProvider: { resolveProvider: false },
          semanticTokensProvider: {
            full: true,
            legend: getSemanticLegend(),
          },
        },
      };
    });

    this.connection.onCompletion((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.completionHandler.handle(params, doc) : [];
    });

    this.connection.onHover((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.hoverHandler.handle(params, doc) : null;
    });

    this.connection.onDefinition((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.definitionHandler.handle(params, doc) : null;
    });

    this.connection.onReferences((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.referenceHandler.handle(params, doc) : [];
    });

    this.connection.onPrepareRename((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      if (!doc) return null;
      const result = this.renameHandler.prepare(params, doc);
      if (!result) return null;
      return { range: result.range, placeholder: result.word };
    });

    this.connection.onRenameRequest((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.renameHandler.handle(params, doc, params.newName) : null;
    });

    this.connection.onCodeAction((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.codeActionHandler.handle(params, doc) : [];
    });

    this.connection.onFoldingRanges((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.foldHandler.handle(doc) : [];
    });

    this.connection.onCodeLens((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? this.codeLensHandler.handle(params, doc) : [];
    });

    this.connection.languages.semanticTokens.on((params) => {
      const doc = this.documents.get(params.textDocument.uri);
      return doc ? computeSemanticTokens(doc) : { data: [] };
    });

    this.documents.onDidChangeContent((change) => {
      this.indexer.updateDoc(change.document.uri, change.document.getText(), change.document.version);
      const diagnostics = this.diagnosticHandler.handle(change.document);
      this.connection.sendDiagnostics({ uri: change.document.uri, diagnostics });
    });
  }
}

new NexyLspServer();
