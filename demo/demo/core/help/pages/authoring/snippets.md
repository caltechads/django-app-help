---
title: Authoring Snippets
summary: Reusable Markdown fragments under help/snippets/.
---

# Authoring Snippets

**Snippets** are small Markdown fragments under `help/snippets/`. They are not browsable on their own — pages pull them in with include directives.

Use snippets for repeated warnings, contact blocks, or shared procedural steps that appear on multiple pages.

To include a snippet from a page:

```markdown
::include snippets/demo-tip.md
```

See [Include directives](help:authoring/includes) for nesting and validation rules.
