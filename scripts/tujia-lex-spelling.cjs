// Reuse the public site's converters; do not invent a general IPA-to-tone map.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(process.argv[2] || '.');
const ctx = vm.createContext({localStorage:{getItem:()=>null},document:{addEventListener(){}},window:{addEventListener(){}}});
for (const name of ['ipa-normalize.js','notation-profiles.js','notation-ui.js','yubao.js','grammar-notation.js']) {
  vm.runInContext(fs.readFileSync(path.join(root,'site',name),'utf8'),ctx,{filename:name});
}
const input = JSON.parse(fs.readFileSync(0,'utf8'));
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
