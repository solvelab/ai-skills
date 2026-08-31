import { spawn } from 'node:child_process'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
const chrome = `${process.env.HOME}/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`
const ids = process.argv.slice(2)
for (const id of ids) {
  const url = pathToFileURL(resolve('one-creature.html')).href + '?id=' + id
  const proc = spawn(chrome, ['--headless=new','--remote-debugging-port=0','--no-sandbox','--window-size=1400,900','--hide-scrollbars', url], {stdio:['ignore','ignore','pipe']})
  const ws = await new Promise((res)=>{let b='';proc.stderr.on('data',c=>{b+=c;const m=b.match(/ws:\/\/[^\s]+/);if(m)res(m[0])})})
  const sock = new WebSocket(ws); await new Promise(r=>sock.addEventListener('open',r))
  let i=1; const pend=new Map()
  sock.addEventListener('message',(e)=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id)}})
  const send=(method,params={},sessionId)=>new Promise(r=>{const n=i++;pend.set(n,r);sock.send(JSON.stringify({id:n,method,params,sessionId}))})
  const {targetInfos} = await send('Target.getTargets')
  const t = targetInfos.find(t=>t.type==='page')
  const {sessionId} = await send('Target.attachToTarget',{targetId:t.targetId,flatten:true})
  await send('Page.enable',{},sessionId); await send('Runtime.enable',{},sessionId)
  for (let k=0;k<80;k++){
    const r = await send('Runtime.evaluate',{expression:'document.readyState',returnByValue:true},sessionId)
    if (r?.result?.value==='complete') break
    await new Promise(r=>setTimeout(r,100))
  }
  await send('Performance.enable',{},sessionId)
  // Without a screencast headless Chrome never composites, so rAF is throttled to nothing and
  // every counter reads zero. The screencast is what makes the page actually run.
  await send('Page.startScreencast',{format:'jpeg',quality:20,everyNthFrame:1},sessionId)
  await new Promise(r=>setTimeout(r,900))
  const a = await send('Performance.getMetrics',{},sessionId)
  await new Promise(r=>setTimeout(r,4000))
  const b = await send('Performance.getMetrics',{},sessionId)
  const g=(m,k)=>m.metrics.find(x=>x.name===k)?.value??0
  const d=(k)=>g(b,k)-g(a,k)
  console.log(`${id.padEnd(11)} layout/s ${(d('LayoutCount')/4).toFixed(1).padStart(6)}   style ms/s ${(d('RecalcStyleDuration')*1000/4).toFixed(2).padStart(7)}   task ms/s ${(d('TaskDuration')*1000/4).toFixed(1).padStart(7)}`)
  sock.close(); proc.kill()
}
