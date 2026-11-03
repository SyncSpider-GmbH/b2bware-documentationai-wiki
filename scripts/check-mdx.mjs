#!/usr/bin/env node
/**
 * Pre-flight check for documentation.ai auto-publish.
 *
 * Catches the failures we have already seen in production:
 *   - MDX/acorn parse errors (unescaped `{{` Blade echoes, broken JSX)
 *   - Unsupported components (`<Note>`, `<Warning>`, …)
 *   - Invalid `<Callout kind="…">` values
 *
 * Usage:
 *   node scripts/check-mdx.mjs              # check the wiki root (cwd/..)
 *   node scripts/check-mdx.mjs --self-test  # run fixture assertions
 *   node scripts/check-mdx.mjs /path/to/wiki
 */
import { compile } from '@mdx-js/mdx'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** documentation.ai Callout kinds — see https://documentation.ai/docs/components/callout */
const ALLOWED_CALLOUT_KINDS = new Set(['info', 'tip', 'success', 'alert', 'danger'])

/** JSX tags documentation.ai rejected (or that are not in their component set). */
const BANNED_TAGS = new Set([
  'Note',
  'Warning',
  'Tip',
  'Info',
  'Check',
  'Accordion',
  'Details',
])

const CALLOUT_KIND_RE = /<Callout\b[^>]*\bkind=["']([^"']+)["']/g
const BANNED_TAG_RE = new RegExp(`</?(${[...BANNED_TAGS].join('|')})\\b`, 'g')
const FENCE_RE = /^[ \t]*(`{3,}|~{3,})/

function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name.startsWith('.')) continue
    if (ent.name === 'node_modules' || ent.name === 'scripts') continue
    const p = path.join(dir, ent.name)
    if (ent.isDirectory()) walk(p, out)
    else if (/\.(md|mdx)$/.test(ent.name)) out.push(p)
  }
  return out
}

/**
 * Yield non-fence lines with original 1-based line numbers.
 * Fenced ``` / ~~~ blocks (including indented) are skipped entirely —
 * Blade samples belong there.
 */
function* contentLines(src) {
  let inFence = false
  let fenceMarker = null
  const lines = src.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const m = FENCE_RE.exec(line)
    if (m) {
      const marker = m[1][0] // ` or ~
      const len = m[1].length
      if (!inFence) {
        inFence = true
        fenceMarker = marker.repeat(len)
      } else if (line.trim().startsWith(fenceMarker[0].repeat(fenceMarker.length))) {
        inFence = false
        fenceMarker = null
      }
      continue
    }
    if (!inFence) yield { lineNo: i + 1, line }
  }
}

function staticFindings(rel, src) {
  const findings = []

  for (const { lineNo, line } of contentLines(src)) {
    // documentation.ai parses .md as MDX. Blade {{ }} outside fences breaks
    // acorn; their table/inline-code handling is also strict, so flag every
    // occurrence outside fences (including inside inline backticks).
    let idx = 0
    while ((idx = line.indexOf('{{', idx)) !== -1) {
      findings.push({
        rel,
        line: lineNo,
        col: idx + 1,
        level: 'error',
        rule: 'no-blade-echo',
        message:
          'Found `{{` outside a fenced code block. documentation.ai parses pages as MDX and acorn rejects Blade/Mustache echoes — rewrite in prose (e.g. "Blade escaped echo") or move the example into a ``` fence.',
      })
      idx += 2
    }

    for (const m of line.matchAll(BANNED_TAG_RE)) {
      findings.push({
        rel,
        line: lineNo,
        col: (m.index ?? 0) + 1,
        level: 'error',
        rule: 'banned-component',
        message: `<${m[1]}> is not a supported documentation.ai component. Use <Callout kind="…"> (info|tip|success|alert|danger) instead.`,
      })
    }

    for (const m of line.matchAll(CALLOUT_KIND_RE)) {
      const kind = m[1]
      if (!ALLOWED_CALLOUT_KINDS.has(kind)) {
        findings.push({
          rel,
          line: lineNo,
          col: (m.index ?? 0) + 1,
          level: 'error',
          rule: 'callout-kind',
          message: `Invalid Callout kind="${kind}". Allowed: ${[...ALLOWED_CALLOUT_KINDS].join(', ')}. (Mintlify-style "warning" → use "alert".)`,
        })
      }
    }
  }

  return findings
}

async function compileFindings(rel, src) {
  try {
    await compile(src, { format: 'mdx', development: true })
    return []
  } catch (e) {
    const msg = (e.message || String(e)).split('\n')[0]
    let line = 0
    let col = 0
    const pos = /(?:line |:)(\d+)(?::|,\s*column\s+)(\d+)/i.exec(e.message || '')
      || /\((\d+):(\d+)\)/.exec(e.message || '')
    if (pos) {
      line = Number(pos[1])
      col = Number(pos[2])
    }
    return [{
      rel,
      line,
      col,
      level: 'error',
      rule: 'mdx-parse',
      message: msg,
    }]
  }
}

async function checkFile(abs, root) {
  const rel = path.relative(root, abs)
  const src = fs.readFileSync(abs, 'utf8')
  return [...staticFindings(rel, src), ...(await compileFindings(rel, src))]
}

async function checkTree(root) {
  const files = walk(root)
  const all = []
  for (const f of files) {
    all.push(...(await checkFile(f, root)))
  }
  return { files: files.length, findings: all }
}

function printFindings(findings) {
  for (const f of findings) {
    const loc = f.line ? `${f.rel}:${f.line}:${f.col}` : f.rel
    console.error(`${f.level.toUpperCase()} [${f.rule}] ${loc}\n  ${f.message}`)
  }
}

async function selfTest() {
  const fixtures = path.join(__dirname, 'fixtures')
  fs.mkdirSync(fixtures, { recursive: true })
  const cases = [
    {
      name: 'blade-echo.md',
      src: `---\ntitle: t\ndescription: d\n---\n\n| a | b |\n| - | - |\n| x | echo {{ $foo }} here |\n`,
      mustInclude: ['no-blade-echo'],
    },
    {
      name: 'banned-note.mdx',
      src: `---\ntitle: t\ndescription: d\n---\n\n<Note>nope</Note>\n`,
      mustInclude: ['banned-component'],
    },
    {
      name: 'bad-callout-kind.mdx',
      src: `---\ntitle: t\ndescription: d\n---\n\n<Callout kind="warning">x</Callout>\n`,
      mustInclude: ['callout-kind'],
    },
    {
      name: 'ok-callout.mdx',
      src: `---\ntitle: t\ndescription: d\n---\n\n<Callout kind="alert">x</Callout>\n\n\`\`\`blade\n{{ $ok_in_fence }}\n\`\`\`\n`,
      mustInclude: [],
    },
  ]

  let failed = 0
  for (const c of cases) {
    const abs = path.join(fixtures, c.name)
    fs.writeFileSync(abs, c.src)
    const findings = await checkFile(abs, fixtures)
    const rules = new Set(findings.map((f) => f.rule))
    const missing = c.mustInclude.filter((r) => !rules.has(r))
    const unexpected = c.mustInclude.length === 0 && findings.length > 0
    if (missing.length || unexpected) {
      failed++
      console.error(`SELF-TEST FAIL ${c.name}`)
      console.error('  expected rules:', c.mustInclude)
      console.error('  got:', [...rules])
      printFindings(findings)
    } else {
      console.log(`SELF-TEST OK ${c.name}`)
    }
  }
  return failed
}

async function main() {
  const args = process.argv.slice(2)
  if (args.includes('--self-test')) {
    const failed = await selfTest()
    process.exit(failed ? 1 : 0)
  }

  const rootArg = args.find((a) => !a.startsWith('--'))
  const root = path.resolve(rootArg || path.join(__dirname, '..'))
  if (!fs.existsSync(root)) {
    console.error(`wiki root not found: ${root}`)
    process.exit(2)
  }

  console.log(`Checking MDX/MD under ${root}`)
  const { files, findings } = await checkTree(root)
  const errors = findings.filter((f) => f.level === 'error')
  printFindings(errors)
  console.log(`checked_files=${files} errors=${errors.length}`)
  process.exit(errors.length ? 1 : 0)
}

main()
