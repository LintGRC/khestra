import { mergeAttributes, Node } from "@tiptap/core";

export interface VariableOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    variable: {
      insertVariable: (name: string) => ReturnType;
    };
  }
}

export const Variable = Node.create<VariableOptions>({
  name: "variable",

  group: "inline",

  inline: true,

  selectable: true,

  atom: true,

  addAttributes() {
    return {
      name: {
        default: null,
        parseHTML: (el) => (el as HTMLElement).getAttribute("data-name"),
        renderHTML: (attrs) => ({ "data-name": attrs.name, class: "policy-variable-chip" }),
      },
    };
  },

  parseHTML() {
    return [{ tag: "span[data-name]" }];
  },

  renderHTML({ HTMLAttributes }) {
    return ["span", mergeAttributes(this.options.HTMLAttributes, HTMLAttributes), "{{", HTMLAttributes["data-name"], "}}"];
  },

  addCommands() {
    return {
      insertVariable:
        (name: string) =>
        ({ chain }) => {
          return chain().insertContent({ type: this.name, attrs: { name } }).run();
        },
    };
  },
});
