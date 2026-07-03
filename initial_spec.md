# File-Based Markdown Help System Specification

## Overview

This project will provide a reusable Django help system backed by Markdown files stored on the filesystem. Help content will be committed to the application’s Git repository, deployed with the application, and served from a read-only container at runtime.

The system is intended for application help, workflow documentation, field explanations, and user-facing operational guidance. It is not intended to replace a full CMS or general documentation platform.

## Goals

The help system should:

- Store help content as Markdown files.
- Keep all help content version-controlled in Git.
- Support read-only production deployments.
- Allow coding agents and developers to easily read and modify help content.
- Provide reusable snippets through a custom Markdown include directive.
- Support multiple user-oriented “books” using YAML definitions.
- Allow the same canonical help page to appear in multiple books.
- Provide validation for broken links, missing includes, and invalid book definitions.



## File Structure

A typical help directory should look like this:

```text
help/
├── books/
│   ├── user.yaml
│   ├── admin.yaml
│   └── developer.yaml
│
├── pages/
│   ├── billing/
│   │   ├── overview.md
│   │   ├── pta-accounts.md
│   │   └── oracle-upload.md
│   │
│   ├── projects/
│   │   ├── overview.md
│   │   └── lifecycle.md
│   │
│   └── security/
│       └── permissions.md
│
├── snippets/
│   ├── pta-warning.md
│   ├── support-contact.md
│   └── common/
│       ├── admin-note.md
│       └── charging-warning.md
│
├── assets/
│   ├── images/
│   └── downloads/
│
└── metadata/
    ├── redirects.yaml
    ├── aliases.yaml
    └── glossary.yaml
```



## Pages

Pages are canonical help topics stored under `help/pages/`.

Each page is a Markdown file. The page path under `pages/` becomes its logical help ID.

For example:

```text
help/pages/billing/pta-accounts.md
```

has the logical ID:

```text
billing/pta-accounts
```

Pages may contain YAML front matter:

```markdown
---
title: PTA Accounts
summary: How PTA accounts are used for billing.
audience:
  - user
  - admin
---

# PTA Accounts

This page explains how PTA accounts are used.
```



## Snippets

Snippets are reusable Markdown fragments stored under `help/snippets/`.

Snippets are not directly browsable as standalone help pages. They are intended to be included inside pages.

Example:

```text
help/snippets/pta-warning.md
```

```markdown
> Charges will be made to the PTA account provided by the requester.
```



## Include Directive

The system will support a custom line-based include directive:

```markdown
::include snippets/pta-warning.md
```

During rendering, include directives are resolved before Markdown is converted to HTML.

The processing order is:

```text
read Markdown page
extract page front matter
expand ::include directives
convert expanded Markdown to HTML
sanitize/post-process HTML
render in Django template
```

An included file’s contents are inserted into the parent document as Markdown, allowing snippets to contain normal Markdown formatting.

Include rules:

- Includes must point to files under `help/snippets/`.
- Absolute paths are not allowed.
- Parent directory traversal such as `../` is not allowed.
- Circular includes must be detected and rejected.
- Include depth should be limited, for example to 5 levels.
- Missing include files should raise an error in development and fail validation in CI.



## Books

Books define curated reading paths or landing pages for different audiences. Books are YAML files stored under `help/books/`.

A book does not own pages. It references canonical page IDs from `help/pages/`.

Example:

```yaml
title: Administrator Guide
slug: admin
description: Help topics for application administrators.

sections:
  - title: Billing
    pages:
      - billing/overview
      - billing/pta-accounts
      - billing/oracle-upload

  - title: Security
    pages:
      - security/permissions
```

A regular user book may reference a smaller subset of the same canonical pages:

```yaml
title: User Guide
slug: user
description: Help topics for regular application users.

sections:
  - title: Getting Started
    pages:
      - billing/overview
      - billing/pta-accounts
```

This allows multiple books to share the same page without duplicating content.

## URLs

The default help home URL should resolve to the appropriate book for the current user:

```text
/help/
```

Book URLs:

```text
/help/books/user/
/help/books/admin/
```

Canonical page URLs:

```text
/help/billing/overview/
/help/billing/pta-accounts/
/help/security/permissions/
```

Book-specific page URLs may optionally be supported:

```text
/help/books/admin/billing/oracle-upload/
```

The canonical page URL should remain the primary URL for a page.

## Internal Links

Internal links should use logical help IDs rather than filesystem paths.

Example:

```markdown
[PTA Accounts](help:billing/pta-accounts)
[Oracle Upload Workflow](help:billing/oracle-upload)
```

These links are converted during rendering into application URLs:

```html
<a href="/help/billing/pta-accounts/">PTA Accounts</a>
```

Anchor links should also be supported:

```markdown
[Valid PTA format](help:billing/pta-accounts#valid-pta-format)
```



## Assets

Assets are stored under `help/assets/`.

Markdown may reference assets using a custom asset link format:

```markdown
![Upload workflow](asset:images/upload-workflow.png)
```

The renderer converts this to the correct served asset URL.

## Permissions and Audience

Books control discovery, but page-level permissions control access.

A page may define audience or permission metadata:

```yaml
audience:
  - admin
permission: billing.view_oracle_upload_help
```

The system should check permissions whenever a page is viewed directly, even if it is not linked from the current user’s book.

## Authorization and Permission Handling

The help system should support application-specific authorization through a configurable permission backend.

Rather than hard-coding permission logic into the library, the application should provide a class responsible for determining whether a given user may view a book, page, or asset.

Example Django setting:

```python
HELP_PERMISSION_BACKEND = "myapp.help.permissions.ApplicationHelpPermissionBackend"
```

The backend class should implement a small interface:

```python
class BaseHelpPermissionBackend:
    def can_view_book(self, user, book) -> bool:
        return True

    def can_view_page(self, user, page) -> bool:
        return True

    def can_view_asset(self, user, asset) -> bool:
        return True
```

The library will call this backend whenever help content is requested.

Example implementation:

```python
class ApplicationHelpPermissionBackend:
    def can_view_book(self, user, book):
        if book.slug == "admin":
            return user.is_staff
        return user.is_authenticated

    def can_view_page(self, user, page):
        permission = page.metadata.get("permission")

        if permission:
            return user.has_perm(permission)

        audience = page.metadata.get("audience", [])

        if "admin" in audience and not user.is_staff:
            return False

        return user.is_authenticated

    def can_view_asset(self, user, asset):
        return user.is_authenticated
```

Page metadata may declare required permissions:

```yaml
---
title: Oracle Uploads
permission: billing.view_oracle_upload_help
audience:
  - admin
---
```

Book metadata may also declare required permissions:

```yaml
title: Administrator Guide
slug: admin
permission: help.view_admin_book
```

Authorization rules:

- Books control discovery and navigation.
- Pages control direct access.
- Hiding a page from a book is not sufficient security.
- The permission backend must be checked for every direct page request.
- If a user cannot access a page, the application may return either `403 Forbidden` or `404 Not Found`, depending on the desired disclosure behavior.
- The default backend should require authentication but otherwise allow all pages, unless stricter behavior is configured.

This approach keeps the help library generic while allowing each Django application to enforce its own authorization model.


## Help Home and Book Resolution

The help system should support resolving the appropriate help home page, or book index, for the current user.

In simple applications, there may be only one book. In that case, `/help/` should always render the single configured default book.

In applications with multiple audiences, such as regular users, administrators, developers, or billing managers, the application should be able to provide a configurable book resolver.

Example Django settings:

```python
HELP_DEFAULT_BOOK = "user"
HELP_BOOK_RESOLVER = "myapp.help.resolvers.ApplicationHelpBookResolver"
```

The resolver class should determine which book should be shown when a user visits:

```text
/help/
```

The resolver does not grant access by itself. It only chooses the most appropriate landing page. Authorization is still handled separately by the permission backend.

Example interface:

```python
class BaseHelpBookResolver:
    def get_book_for_user(self, user, request=None) -> str:
        return settings.HELP_DEFAULT_BOOK
```

Example implementation:

```python
class ApplicationHelpBookResolver:
    def get_book_for_user(self, user, request=None):
        if user.is_superuser or user.groups.filter(name="Help Administrators").exists():
            return "admin"

        if user.has_perm("billing.view_billing_admin_help"):
            return "billing-manager"

        return "user"
```

With this configuration:

```text
/help/
```

may resolve to one of:

```text
/help/books/user/
/help/books/admin/
/help/books/billing-manager/
```

depending on the current user.

If `HELP_BOOK_RESOLVER` is not configured, the library should use `HELP_DEFAULT_BOOK`.

If there is only one book in `help/books/`, the system may use that book automatically.

Resolution rules:

- `/help/` resolves to the most appropriate book for the current user.
- The resolver returns a book slug, not a filesystem path.
- The returned book must exist in `help/books/`.
- The returned book must still pass authorization checks.
- If the resolved book does not exist, the system should raise a configuration error.
- If the user is not allowed to view the resolved book, the system may fall back to another allowed book or return `403 Forbidden`.
- Book resolution should not be used as a security boundary.

This allows applications to provide a tailored help landing page while keeping the help library generic.


## Validation

The library should provide a Django management command:

```bash
python manage.py validate_help
```

Validation should check:

- all book YAML files are valid
- all pages referenced by books exist
- all `help:` links resolve
- all `asset:` links resolve
- all `::include` targets exist
- no circular includes exist
- no include exceeds max depth
- all pages have required metadata
- no duplicate page IDs exist
- no protected pages are exposed through inappropriate books



## Runtime Behavior

In production, help content is considered immutable. Rendered pages may be cached aggressively.

In development, the system may reload files on each request or use file modification times to avoid restarting the server after help edits.

## Non-Goals

This system is not intended to provide:

- runtime editing of help content
- database-backed documentation
- full CMS functionality
- collaborative rich-text editing
- replacement for Sphinx, MkDocs, or Confluence



## Summary

The proposed help system is a Git-backed, Markdown-based Django application help library. It uses canonical Markdown pages, reusable snippets, YAML-defined books, and safe pre-render include expansion. This design keeps help content close to the application code, supports read-only deployments, and makes the documentation easy for both developers and coding agents to maintain.