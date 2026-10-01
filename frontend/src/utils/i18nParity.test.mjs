// Session 18 hotfix — EN/FR string parity pin (run: npm run test:i18n).
//
// Pure Node, no dependency: loads both locale files and asserts
//   1. identical key paths (flat dotted keys AND nested objects are handled),
//   2. every leaf is a non-empty string in both languages,
//   3. the lesson/review keys used by the hotfix flows exist in both.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const HERE = dirname(fileURLToPath(import.meta.url))
const I18N = join(HERE, '..', 'i18n')

const en = JSON.parse(readFileSync(join(I18N, 'en.json'), 'utf8'))
const fr = JSON.parse(readFileSync(join(I18N, 'fr.json'), 'utf8'))

let passed = 0
function check(name, fn) {
  try {
    fn()
    passed++
    console.log(`ok - ${name}`)
  } catch (err) {
    console.error(`FAIL - ${name}`)
    console.error(err)
    process.exitCode = 1
  }
}

/** Flatten nested locale objects into dotted key paths -> leaf values. */
function flatten(node, prefix = '', out = new Map()) {
  for (const [key, value] of Object.entries(node)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      flatten(value, path, out)
    } else {
      out.set(path, value)
    }
  }
  return out
}

const enFlat = flatten(en)
const frFlat = flatten(fr)

// The lesson/review keys the hotfix flows render (both languages required).
const REQUIRED_KEYS = [
  'learn.backToLessons',
  'learn.question',
  'learn.score',
  'learn.correct',
  'learn.incorrect',
  'learn.reviewConcept',
  'learn.addedToReview',
  'learn.continueNext',
  'learn.upNextPrefix',
  'learn.lessonComplete',
  'learn.retryMissedHint',
  'review.title',
  'review.readyNow',
  'review.reviewNow',
  'review.nextCard',
  'review.nextDue',
  'review.dueAgainNow',
  'review.allCaughtUp',
  'review.backToLessons',
]

check('EN and FR expose identical key paths (parity)', () => {
  const missingInFr = [...enFlat.keys()].filter((k) => !frFlat.has(k))
  const missingInEn = [...frFlat.keys()].filter((k) => !enFlat.has(k))
  assert.deepEqual(missingInFr, [], `missing in fr.json: ${missingInFr}`)
  assert.deepEqual(missingInEn, [], `missing in en.json: ${missingInEn}`)
})

check('every EN/FR leaf is a non-empty string', () => {
  for (const [lang, flat] of [['en', enFlat], ['fr', frFlat]]) {
    for (const [path, value] of flat) {
      assert.equal(typeof value, 'string', `${lang}.${path} is not a string`)
      assert.ok(value.trim().length > 0, `${lang}.${path} is empty`)
    }
  }
})

check('every lesson/review key used by the hotfix flows exists in both', () => {
  for (const key of REQUIRED_KEYS) {
    assert.ok(enFlat.has(key), `en.json is missing ${key}`)
    assert.ok(frFlat.has(key), `fr.json is missing ${key}`)
  }
})

console.log(`\n${passed} checks passed`)
