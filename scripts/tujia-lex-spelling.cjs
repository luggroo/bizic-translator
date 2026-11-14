// Reuse the public site's converters; do not invent a general IPA-to-tone map.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(process.argv[2] || '.');
const siteRoot = process.argv.includes('--site-root') ? root : path.join(root, 'site');
const ctx = vm.createContext({localStorage:{getItem:()=>null},document:{addEventListener(){}},window:{addEventListener(){}}});
const modules = ['ipa-normalize.js','notation-profiles.js','notation-ui.js','southern-notation.js','yubao.js','grammar-notation.js'];
if (process.argv.includes('--static')) modules.push('lexical-reviews.js','spelling-boundaries.js');
for (const name of modules) {
  vm.runInContext(fs.readFileSync(path.join(siteRoot,name),'utf8'),ctx,{filename:name});
}
const input = JSON.parse(fs.readFileSync(0,'utf8'));
// Export-time conversion: isolate each witness before using the same spelling
// selector as the site. A merged entry must not donate another witness's form.
if (process.argv.includes('--static')) {
  const output = input.words.flatMap(entry => (entry.attestations || []).map(att => {
    const notations = Object.fromEntries(Object.entries(entry.notations || {}).map(([scheme, values]) =>
      [scheme, values.filter(value => value.attestationIds?.includes(att.id))]));
    const word = {id: entry.id, dialect: att.dialect, attestations: [att], notations};
    ctx.initializeSpellingBoundaries({words: [word]});
    const forms = [...(notations.accent || []), ...ctx.completeSpellings(word)].filter(value =>
      value.text && !/[□⟦⟧⁇?]/u.test(value.text) && !value.ambiguous
    ).map(value => ({text: value.text, method: value.method || 'site-converter',
      profile: value.profile || att.source}));
    const ipa = [...new Set(ctx.notationValues(word, 'ipa').map(value => value.text).filter(Boolean))];
    return {attestation_id: att.id, accent: forms, ipa};
  }));
  process.stdout.write(JSON.stringify(output) + '\n');
} else {
// The site's compact UI replaces unresolved spans with a square. Reports need
// their actual wording, so convert each span's contents and retain its brackets.
function accentPreservingGaps(text) {
  return text.split(/(⟦[^⟧]*⟧)/u).map(part => part.startsWith('⟦')
    ? '⟦'+ctx.yeToAccent(part.slice(1,-1))+'⟧' : ctx.yeToAccent(part)).join('');
}
const output = input.map(item => {
  try {
    if (item.mode === 'ye') return {original:item.text,ye:item.text,accent:accentPreservingGaps(item.text)};
    if (item.mode === 'grammar') return {original:item.text,...ctx.grammarSpelling(item.text,'north',item.ye||'')};
    const result = ctx.convertNotation(item.text,item.source);
    return {original:item.text,...result,rows:result.rows?.map(r=>({...r,accent:r.accent||accentPreservingGaps(r.ye)}))};
  } catch (error) { return {original:item.text,error:error.message}; }
});
process.stdout.write(JSON.stringify(output,null,2)+'\n');
}
