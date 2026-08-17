---
title: Server data & auth
description: "@fetch server-side HTTP, @storefrontAuthToken, and the backend API reference."
---

<Info>
This page also ships inside the default theme download under `docs/08-fetch-auth.md`, so offline and AI-assisted authors have the same contract locally. This online version is always the latest.
</Info>

## 9.12 Server-side data — `@fetch`

`@fetch` runs an HTTP request **on the server while the page renders** and assigns the decoded
response to a variable, so you can load data before you output it and then render it with ordinary
`@if` / `@foreach` / `data_get()`.

```blade
@fetch('https://api.example.com/v1/posts?status=published', [
    'headers' => ['Authorization' => 'Bearer sk_live_…'],
    'cache'   => 60,
], 'posts')

@if($posts && !empty($posts['data']))
    <div class="grid gap-4">
        @foreach($posts['data'] as $post)
            <article>
                <h2>{{ data_get($post, 'title') }}</h2>
                <p>{{ data_get($post, 'author.name', 'Staff') }}</p>
            </article>
        @endforeach
    </div>
@endif
```

The **last argument is the variable name** (a plain string literal). Everything before it is the
URL and an optional options array.

### ⚠️ The most important rule — you are publishing whatever you fetch

Anything you fetch and render is placed on a **public page**. `@fetch` can reach data that must
**never** be shown to visitors, so **before you render any fetched value, confirm it is safe to be
public.** This is the single most important rule on this page.

- **NEVER** fetch and render personal or private data — customers, orders, addresses, emails, phone
  numbers, payment details, tokens, or anything tied to a specific person — onto a storefront page.
- **Confirm every internal URL.** An internal `@fetch('/api/...')` call runs with the store's own
  installation context, so it can read far more than a catalog. For each one ask: *"Is every field
  this endpoint returns safe for an anonymous visitor to see?"* If you are not 100% sure, don't use it.
- **NEVER echo a credential.** The token in `headers` is evaluated on the server and never reaches
  the browser — keep it that way. Don't print it, don't put it in an HTML attribute, don't pass it
  to JavaScript.
- Treat `@fetch` as a publishing tool, not a private API client.

### Two forms

**External — an absolute `https://…` URL.** You supply any authentication yourself, in `headers`;
nothing is added for you. The request is SSRF-guarded: only `http`/`https`, and the host may not
resolve to a private / loopback / internal address.

```blade
@fetch('https://api.example.com/feed', ['headers' => ['Authorization' => 'Bearer …']], 'feed')
```

To read DataHub data this way, mint a **read-only API token** scoped to what you need and pass it as
the `Authorization` header — you stay in control of exactly what it can see.

**Internal — a leading-slash `/api/...` path.** The platform rewrites it to this store's own API and
**attaches the visitor's `installation-key` automatically** (and their `x-auth-token` when they're
logged in), so you never type the key. The call runs as the **current visitor** through the normal
controllers — exactly what the storefront app itself receives. It defaults to **GET**; set `method`
(e.g. `POST`) for a read-shaped endpoint that takes a request body — such as real-time pricing. The
platform still authorizes the request as the visitor, so it can only do what their own identity is
already allowed to do — never wire a state-changing write to a plain page render.

```blade
@fetch('/api/v1/apps/product-hub/products?per_page=12&include=mainMedia,price', [], 'catalog')

@if($catalog && !empty($catalog['data']))
    @foreach($catalog['data'] as $product)
        @include('components.product-card', ['product' => $product])
    @endforeach
@endif
```

> The internal form is a convenience for **not repeating the installation key** — it grants no extra
> access and never skips the controller. You still own the rule above: confirm every endpoint you
> call returns only publicly-safe data.

### Options

| Key | Default | Purpose |
| --- | ------- | ------- |
| `method` | `GET` | HTTP method (e.g. `POST`). Works for both forms; internal calls are still authorized as the visitor. |
| `headers` | `[]` | Request headers (external auth goes here). Internal calls force the visitor's `installation-key` / `x-auth-token` and ignore those two if you pass them. |
| `query` | `[]` | Extra query parameters merged into the URL. |
| `json` | — | Request body sent as JSON (any non-GET call). |
| `body` | — | Raw request body (any non-GET call). |
| `timeout` | config | Per-call total timeout, in seconds. |
| `cache` | `0` (off) | Cache the decoded result for N seconds (tenant-scoped). Use it for slow or rate-limited APIs. |
| `as` | `json` | `json` → decoded array; `string` → raw body; `response` → `['ok','status','headers','body','json']`. |
| `throw` | `false` | Re-raise on failure instead of returning `null`. |

### Return value

- **`json` (default):** the decoded JSON body as an array — use `data_get($x, 'a.b')` and `@foreach`.
- **`string`:** the raw body (non-JSON endpoints).
- **`response`:** an envelope with `ok`, `status`, `headers`, `body`, `json`.
- A non-2xx response still returns its decoded body (so you can inspect it). A hard failure (timeout,
  blocked host, connection error) returns **`null`** and the page keeps rendering — so always guard
  with `@if($data)`.

### Do / don't

- ✅ Fetch a public blog feed, a public product list, a public FAQ collection, an external public API.
- ✅ Guard every render: `@if($data) … @endif` (a failed fetch is `null`).
- ✅ Cache slow / external calls with `'cache' => N`.
- ❌ `@fetch('/api/v1/apps/customer-hub/customers', …)` or any customer / order / PII endpoint.
- ❌ `{{ $apiToken }}` or `data-token="{{ … }}"` — never expose a credential to the browser. The **only** sanctioned exception is `@storefrontAuthToken` (§9.14), which issues a short-lived token expressly for initializing a first-party widget.
- ❌ Relying on `@fetch` for a write — internal is GET-only; use a `@storefrontForm` for actions.

---

## 9.14 Authenticated widgets — `@storefrontAuthToken`

Most themes never touch a credential. The exception is a **trusted first-party client-side widget** — a small JS app you embed that must talk to the platform API **as the logged-in customer**. The storefront session lives in an **HttpOnly** cookie that JavaScript cannot read, and a widget's API host is usually a different domain than the storefront, so that cookie is never sent to it anyway. `@storefrontAuthToken` is the one sanctioned bridge: it hands the widget a **short-lived token for the current customer** — and nothing else.

### What it emits

A **short-lived (1 hour) `x-auth-token`** for the currently logged-in customer, or an **empty string** for guests. It never emits the long-lived session cookie — only this bounded token.

- **Reused** across page loads while the token still has time left (tracked server-side in an HttpOnly cookie); a fresh token is minted only when the previous one is missing or near expiry, so refreshing the page does not churn tokens.
- **Guest-safe:** for a visitor who is not logged in it emits `''`, so your loader can simply skip the authenticated path.

### Usage

Read it once in your widget loader and pass it as the widget's `api_key`:

```blade
<div id="my-widget"></div>

<script type="module">
    const token = '@storefrontAuthToken';
    const { default: widget } = await import('https://cdn.example.com/widget.js');

    widget.render({
        selector: '#my-widget',
        // Authenticated when logged in; empty string falls back to guest behaviour.
        ...(token ? { api_key: token } : {}),
    });
</script>
```

The widget then sends that value as the `x-auth-token` header on its own API calls (see §9.15) and is treated as the customer.

### Security — read this

- This is the **only** place a theme may put a credential in the browser. It is safe *because* the token is short-lived (1h) and is **not** the session cookie — the session stays HttpOnly.
- Use it **only** to initialize a **trusted first-party** widget's `api_key`. Never hand it to a third-party script.
- **Never log it**, never write it into a URL, and never place it in a `data-*` attribute or any other DOM sink you don't control. Read it into a module-scoped `const` and pass it straight to the widget.

---

## 9.15 API documentation — the backend reference

A storefront theme is **Blade only**: the platform renders pages server-side and the global view data (`$cart`, `$me`, `$rootCategories`, …) is all a theme needs. As a rule you **never call the API from client-side JavaScript and never put a token in the page** — the single sanctioned exception is a trusted first-party widget initialized with `@storefrontAuthToken` (§9.14). When you genuinely need backend data inside a page, fetch it **server-side** with `@fetch` (§9.12).

For the endpoints, request bodies and responses behind those data flows, the **single source of truth** is the hosted API reference:

- **https://b2bware.documentationai.com/api-reference** — one page per endpoint, grouped by hub (AuthHub, ProductHub, OrderHub, CustomerHub, …).
- Server: **`https://api.datahub.syncspider.com`** (`/api/v1/apps/<hub-slug>/…`).
- Auth: an `installation-key` header (your tenant) plus an `x-auth-token` for customer-scoped calls — e.g. [AuthHub → Login](https://b2bware.documentationai.com/api-reference/auth-hub/post-api-v1-apps-auth-hub-login).

That site is the only API documentation you need; do not rely on any other copy. If something is missing there, ask the platform team rather than guessing an endpoint.

---
