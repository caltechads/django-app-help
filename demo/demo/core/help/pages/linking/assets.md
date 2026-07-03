---
title: Asset Links
summary: Reference images and downloads under help/assets/.
---

# Asset Links

Store images and downloads under `help/assets/`. Reference them with the `asset:` prefix:

```markdown
![Help content layout](asset:images/help-diagram.png)
```

The diagram below is served from the demo help tree:

![Help content layout](asset:images/help-diagram.png)

Asset paths must not traverse outside `help/assets/`. Missing files fail validation.
