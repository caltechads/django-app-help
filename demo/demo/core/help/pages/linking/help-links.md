---
title: Help Links
summary: "Cross-reference other pages with help: URLs."
---

# Help Links

Link to other help pages with logical IDs instead of filesystem paths:

```markdown
[Pages overview](help:topics/pages)
```

The renderer converts these to application URLs when Django views are wired.

## Anchor links

Link to a heading on another page:

```markdown
[Authoring pages](help:authoring/pages#front-matter)
```

All `help:` targets must resolve to an existing page file. Validation fails the build when a link is broken.
