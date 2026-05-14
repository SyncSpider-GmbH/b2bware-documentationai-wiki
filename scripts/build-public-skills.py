#!/usr/bin/env python3
"""
Build three public AI skills (datahub-core, datahub-hubs, datahub-storefront)
from the Mintlify docs MDX sources.

Output:
  dist/skills/datahub-core/        SKILL.md + references/*.md + openapi/*.yaml
  dist/skills/datahub-hubs/        SKILL.md + references/*.md + openapi/*.yaml
  dist/skills/datahub-storefront/  SKILL.md + references/*.md
  dist/skills/datahub-core-<ver>.zip, datahub-hubs-<ver>.zip, datahub-storefront-<ver>.zip

Usage:
  python3 scripts/docs/build-public-skills.py [--version 1.0.0]

The script is idempotent — dist/ is wiped and rebuilt on every run.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT
DIST = REPO_ROOT / "dist" / "skills"

# ---------------------------------------------------------------------------
# Skill manifests — which MDX files go where, and the SKILL.md description.
# ---------------------------------------------------------------------------

@dataclass
class SkillSpec:
    name: str
    description: str
    overview: str
    # Each tuple: (output filename, source MDX path relative to DOCS_ROOT, table label)
    pages: list[tuple[str, str, str]]
    # OpenAPI yamls (relative to DOCS_ROOT) → copied to openapi/ in the skill
    openapi: list[str]


SKILLS: list[SkillSpec] = [
    SkillSpec(
        name="datahub-core",
        description=(
            "Use when integrating with the B2Bware DataHub API and you need cross-cutting fundamentals — "
            "authentication (bearer tokens, installation key, storefront customer auth, CORS), filtering syntax, "
            "includes, pagination (per_page, total_pages), pricing, media/CDN URLs, webhooks, idempotency, "
            "rate limiting, versioning, environments, and error handling. Triggers on any DataHub API task that "
            "is not specific to a single hub or to the storefront flow."
        ),
        overview=(
            "Foundational reference for any DataHub API integration. Read `references/01-authentication.md` "
            "first, then load only the topic-specific guide(s) you need. The OpenAPI spec for AuthHub is shipped "
            "in `openapi/` so an AI assistant can resolve exact request/response shapes for login, register, "
            "and password-reset endpoints."
        ),
        pages=[
            ("01-authentication.md", "authentication.mdx", "Overview of all auth flows"),
            ("02-storefront-customer-auth.md", "authentication/storefront-customer.mdx", "Storefront login/register"),
            ("03-installation-key.md", "authentication/installation-key.mdx", "Tenant installation key header"),
            ("04-server-to-server.md", "authentication/server-to-server.mdx", "Service tokens for ERP/sync"),
            ("05-cors.md", "authentication/cors-and-browsers.mdx", "Browser-based CORS rules"),
            ("06-common-patterns.md", "core-concepts/common-patterns.mdx", "Pagination, sorting, response shapes"),
            ("07-filtering.md", "core-concepts/filtering.mdx", "JSON filter syntax (CommonFilterRepository)"),
            ("08-includes.md", "core-concepts/includes.mdx", "Eager-load relations via ?include"),
            ("09-recommended-includes.md", "core-concepts/recommended-includes.mdx", "Per-hub include cheat sheet"),
            ("10-pricing.md", "core-concepts/pricing.mdx", "List / final / special price resolution"),
            ("11-media-urls.md", "core-concepts/media-urls.mdx", "Absolute CDN URLs + transforms"),
            ("12-webhooks.md", "core-concepts/webhooks.mdx", "EventHub delivery contract"),
            ("13-idempotency.md", "core-concepts/idempotency.mdx", "Safe retries"),
            ("14-versioning.md", "core-concepts/versioning.mdx", "API versioning policy"),
            ("15-environments.md", "core-concepts/environments.mdx", "Dev/staging/prod URLs"),
            ("16-error-handling.md", "core-concepts/error-handling.mdx", "HTTP status conventions"),
            ("17-rate-limiting.md", "help-center/troubleshooting/rate-limiting.mdx", "400 req/min throttle"),
        ],
        openapi=["api-reference/auth-hub/openapi.yaml"],
    ),
    SkillSpec(
        name="datahub-hubs",
        description=(
            "Use when calling specific B2Bware DataHub hub endpoints — ProductHub (catalog/stock/prices), "
            "OrderHub (orders/checkout), CustomerHub (accounts/addresses), AttributesHub, MediaHub, NotificationHub, "
            "TaxHub, SettingsHub, LicenseHub, AuthHub, EventHub (webhooks), RuleHub (promotions/coupons). "
            "Each hub has a reference page describing its endpoints, plus a full OpenAPI 3.0 spec for exact "
            "request/response shapes. Triggers on tasks naming a hub or a hub-specific resource (products, "
            "orders, customers, attributes, media, notifications, taxes, settings, licenses, events, rules, coupons)."
        ),
        overview=(
            "Endpoint reference for every active DataHub hub. Read `references/00-hub-overview.md` first to map "
            "responsibilities, then load the specific hub guide. OpenAPI 3.0 specs live in `openapi/` — point your "
            "AI assistant at them for exact paths, parameters, request bodies, and response schemas."
        ),
        pages=[
            ("00-hub-overview.md", "hubs/overview.mdx", "Which hub owns what"),
            ("01-product-hub.md", "hubs/product-hub.mdx", "Catalog, stock, prices, media"),
            ("02-order-hub.md", "hubs/order-hub.mdx", "Orders, payments, shipments"),
            ("03-customer-hub.md", "hubs/customer-hub.mdx", "Accounts, addresses, groups"),
            ("04-attributes-hub.md", "hubs/attributes-hub.mdx", "Dynamic product attributes"),
            ("05-media-hub.md", "hubs/media-hub.mdx", "Files, images, CDN"),
            ("06-notification-hub.md", "hubs/notification-hub.mdx", "Email, SMS, push, in-app"),
            ("07-tax-hub.md", "hubs/tax-hub.mdx", "Tax classes and jurisdictions"),
            ("08-settings-hub.md", "hubs/settings-hub.mdx", "Config, translations, locales"),
            ("09-license-hub.md", "hubs/license-hub.mdx", "License pools and assignments"),
            ("10-auth-hub.md", "hubs/auth-hub.mdx", "Session and impersonation"),
            ("11-event-hub.md", "hubs/event-hub.mdx", "Webhook subscriptions"),
            ("12-rule-hub.md", "hubs/rule-hub.mdx", "Promotions, coupons, shipping rates"),
        ],
        openapi=[
            "api-reference/product-hub/openapi.yaml",
            "api-reference/order-hub/openapi.yaml",
            "api-reference/customer-hub/openapi.yaml",
            "api-reference/attributes-hub/openapi.yaml",
            "api-reference/media-hub/openapi.yaml",
            "api-reference/notification-hub/openapi.yaml",
            "api-reference/tax-hub/openapi.yaml",
            "api-reference/settings-hub/openapi.yaml",
            "api-reference/license-hub/openapi.yaml",
            "api-reference/auth-hub/openapi.yaml",
            "api-reference/event-hub/openapi.yaml",
            "api-reference/rule-hub/openapi.yaml",
        ],
    ),
    SkillSpec(
        name="datahub-storefront",
        description=(
            "Use when building a B2Bware DataHub-powered storefront — browsing the catalog, product detail pages, "
            "cart and checkout flow, customer account area, post-purchase (order status, invoices, downloads). "
            "Covers the exact headers (installation-key, x-auth-token, session-uuid, language-code), pagination, "
            "includes, and stitching across ProductHub / OrderHub / CustomerHub / RuleHub. Triggers on tasks "
            "involving storefront UI, headless commerce, B2B portals, guest carts, or buyer-side integration."
        ),
        overview=(
            "End-to-end storefront playbook. Start with `references/00-quickstart.md` for a working integration "
            "in minutes, then drill into the specific page or flow you are building. Pair this with "
            "`datahub-core` for auth/filter/pagination fundamentals and `datahub-hubs` for endpoint-level detail."
        ),
        pages=[
            ("00-quickstart.md", "quickstart.mdx", "Smallest end-to-end integration"),
            ("01-browse-catalog.md", "advanced/storefront/browse-catalog.mdx", "Listing, filters, pagination"),
            ("02-product-detail.md", "advanced/storefront/product-detail.mdx", "PDP with variations + media"),
            ("03-cart-and-checkout.md", "advanced/storefront/cart-and-checkout.mdx", "Cart → payment → order"),
            ("04-customer-account.md", "advanced/storefront/customer-account.mdx", "Profile, addresses, password"),
            ("05-post-purchase.md", "advanced/storefront/post-purchase.mdx", "Orders, invoices, downloads"),
            ("06-checkout-flow.md", "advanced/checkout-flow.mdx", "Deeper checkout state machine"),
            ("07-product-variations.md", "advanced/product-variations.mdx", "Configurable products"),
            ("08-tax-calculation.md", "advanced/tax-calculation.mdx", "Cart-time tax resolution"),
        ],
        openapi=[],
    ),
]


# ---------------------------------------------------------------------------
# MDX → plain Markdown cleaning
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
JSX_OPEN_RE = re.compile(r"<([A-Z][A-Za-z0-9]*)([^/>]*)>")
JSX_CLOSE_RE = re.compile(r"</([A-Z][A-Za-z0-9]*)>")
JSX_SELFCLOSE_RE = re.compile(r"<([A-Z][A-Za-z0-9]*)([^>]*)/>")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body without frontmatter)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[match.end():]


def mdx_to_markdown(body: str) -> str:
    """Strip Mintlify-specific JSX so a plain Markdown reader still gets the content."""
    body = HTML_COMMENT_RE.sub("", body)

    # <Callout kind="warning" title="..."> ... </Callout>   →   > **Warning — title**\n> ...
    def callout_replace(match: re.Match) -> str:
        attrs = match.group(2)
        kind = re.search(r'kind\s*=\s*"([^"]+)"', attrs)
        title = re.search(r'title\s*=\s*"([^"]+)"', attrs)
        label_parts = []
        if kind:
            label_parts.append(kind.group(1).capitalize())
        if title:
            label_parts.append(title.group(1))
        label = " — ".join(label_parts) if label_parts else "Note"
        return f"\n> **{label}**\n"

    body = re.sub(
        r"<Callout([^>]*)>(.*?)</Callout>",
        lambda m: callout_replace(m) + ("> " + m.group(2).strip().replace("\n", "\n> ")) + "\n",
        body,
        flags=re.DOTALL,
    )

    # <Tabs> / <Tab title="X" icon="..."> → ### X  (so each tab becomes a subsection)
    def tab_open(match: re.Match) -> str:
        title = re.search(r'title\s*=\s*"([^"]+)"', match.group(1))
        return f"\n### {title.group(1) if title else 'Section'}\n"

    body = re.sub(r"<Tab\b([^>]*)>", tab_open, body)
    body = re.sub(r"</Tab>", "", body)
    body = re.sub(r"<Tabs\b[^>]*>", "", body)
    body = re.sub(r"</Tabs>", "", body)

    # Remaining JSX components — drop the tags, keep the inner text.
    body = JSX_SELFCLOSE_RE.sub("", body)
    body = JSX_OPEN_RE.sub("", body)
    body = JSX_CLOSE_RE.sub("", body)

    # Collapse 3+ blank lines.
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def render_page(mdx_path: Path, output_name: str) -> str:
    raw = mdx_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    title = meta.get("title") or output_name.removesuffix(".md").replace("-", " ").title()
    description = meta.get("description", "")
    md = mdx_to_markdown(body)
    header = f"# {title}\n\n"
    if description:
        header += f"> {description}\n\n"
    return header + md


# ---------------------------------------------------------------------------
# Skill emission
# ---------------------------------------------------------------------------

def build_skill(spec: SkillSpec, version: str) -> Path:
    out_dir = DIST / spec.name
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "references").mkdir(parents=True)
    if spec.openapi:
        (out_dir / "openapi").mkdir()

    # 1. References
    table_rows = []
    for filename, src, label in spec.pages:
        mdx_path = DOCS_ROOT / src
        if not mdx_path.exists():
            print(f"  ⚠ missing source: {src}", file=sys.stderr)
            continue
        (out_dir / "references" / filename).write_text(
            render_page(mdx_path, filename), encoding="utf-8"
        )
        table_rows.append(f"| {label} | `references/{filename}` |")

    # 2. OpenAPI
    for spec_path in spec.openapi:
        src = DOCS_ROOT / spec_path
        if not src.exists():
            print(f"  ⚠ missing openapi: {spec_path}", file=sys.stderr)
            continue
        dest = out_dir / "openapi" / f"{Path(spec_path).parent.name}.yaml"
        shutil.copy(src, dest)

    # 3. SKILL.md
    skill_md = f"""---
name: {spec.name}
description: {spec.description}
version: {version}
---

# {spec.name}

{spec.overview}

## Progressive Disclosure

Read only what the current task needs. References are short, topic-focused, and renderable as plain Markdown.

| Topic | File |
|---|---|
{chr(10).join(table_rows)}
"""

    if spec.openapi:
        skill_md += "\n## OpenAPI Specs\n\nMachine-readable OpenAPI 3.0 specs are shipped in `openapi/`. Point your AI assistant or HTTP client at them for exact request/response shapes:\n\n"
        for spec_path in spec.openapi:
            slug = Path(spec_path).parent.name
            skill_md += f"- `openapi/{slug}.yaml`\n"

    skill_md += f"""
## Source

Built from the public docs at https://github.com/SyncSpider-GmbH/b2bware-documentationai-wiki — version {version}.
Regenerate with `python3 scripts/docs/build-public-skills.py`.
"""

    (out_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return out_dir


def zip_skill(skill_dir: Path, version: str) -> Path:
    zip_path = DIST / f"{skill_dir.name}-{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in skill_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(skill_dir.parent))
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="1.0.0")
    args = parser.parse_args()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    print(f"Building public skills v{args.version} → {DIST}")
    for spec in SKILLS:
        print(f"  → {spec.name}")
        skill_dir = build_skill(spec, args.version)
        zip_path = zip_skill(skill_dir, args.version)
        print(f"    SKILL.md, {len(spec.pages)} references, {len(spec.openapi)} openapi → {zip_path.name}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
