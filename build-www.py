# Gera www/index.html a partir da versão web (rotina-gabriel.html), adicionando o modo nativo Android.
import re,sys
src=open(sys.argv[1]).read()

head='''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#131619">
'''
fonts='''<style>
@font-face{font-family:'Lexend';font-weight:400;font-display:swap;src:url(fonts/lexend-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Lexend';font-weight:500;font-display:swap;src:url(fonts/lexend-latin-500-normal.woff2) format('woff2')}
@font-face{font-family:'Lexend';font-weight:600 700;font-display:swap;src:url(fonts/lexend-latin-600-normal.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:400;font-display:swap;src:url(fonts/atkinson-hyperlegible-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:700;font-display:swap;src:url(fonts/atkinson-hyperlegible-latin-700-normal.woff2) format('woff2')}
html{-webkit-text-size-adjust:100%}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font-size:16px}
img{max-width:100%}
</style>
'''
# remove Google Fonts (o app funciona offline)
src=re.sub(r'<link rel="preconnect"[^>]*>\n?','',src)
src=re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n?','',src)
src=src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
title,rest=src.split('\n',1)
out=head+title+'\n'+fonts+rest.replace('<script>\n(()=>{','</head>\n<body>\n<script src="capacitor-core.js"></script>\n<script src="local-notifications.js"></script>\n<script>\n(()=>{',1)

def rep(a,b,count=1):
    global out
    if a not in out: sys.exit('NÃO ACHEI: '+a[:70])
    out=out.replace(a,b,count)

# ---------- módulo nativo ----------
NATIVE='''
/* ---------- Android: notificações nativas (funcionam com o app fechado) ---------- */
const CAP=window.Capacitor;const NATIVE=!!(CAP&&CAP.isNativePlatform&&CAP.isNativePlatform());
const LN=NATIVE&&window.capacitorLocalNotifications?window.capacitorLocalNotifications.LocalNotifications:null;
let nativePerm='prompt';const nativeOK=()=>!!LN&&nativePerm==='granted';
const CH='rotina';
async function nativeInit(ask){if(!LN)return;try{let p=await LN.checkPermissions();if(p.display!=='granted'&&ask)p=await LN.requestPermissions();nativePerm=p.display;
 await LN.createChannel({id:CH,name:'Rotina do Gabriel',description:'Lembretes e fim das etapas',importance:4,visibility:1,vibration:true,lights:true});
 LN.addListener&&LN.addListener('localNotificationActionPerformed',()=>{render();if(S.active)openFocus()});
 await syncNativeReminders();await syncTimerNotifs()}catch(e){console.warn('notif',e)}}
async function cancelRange(a,b){if(!LN)return;try{const p=await LN.getPending();const ids=p.notifications.filter(n=>n.id>=a&&n.id<=b).map(n=>({id:n.id}));if(ids.length)await LN.cancel({notifications:ids})}catch(e){}}
async function syncNativeReminders(){if(!nativeOK())return;await cancelRange(1000,1999);const list=[];let id=1000;
 const add=(t,wd)=>{const m=toMin(t.start);list.push({id:id++,channelId:CH,title:RMSG[t.remind]||t.name,body:t.name+' · '+fmtDur(t.dur)+'. Toque para abrir.',schedule:{on:{weekday:wd,hour:Math.floor(m/60),minute:m%60},allowWhileIdle:true},extra:{taskId:t.id}})};
 for(const t of S.weekday)if(t.remind&&S.notif[t.remind])for(const wd of [2,3,4,5,6])add(t,wd);
 for(const t of S.saturday)if(t.remind&&S.notif[t.remind])add(t,7);
 for(const t of S.sunday)if(t.remind&&S.notif[t.remind])add(t,1);
 try{if(list.length)await LN.schedule({notifications:list})}catch(e){console.warn(e)}}
async function syncTimerNotifs(){if(!LN)return;await cancelRange(9000,9099);const a=S.active;if(!nativeOK()||!a||a.pausedAt)return;
 const base=a.startedAt+(a.pausedTotal||0),now=Date.now(),list=[];const at=ms=>new Date(base+ms);
 const endMs=a.planned*60000;
 if(S.warnBefore>0&&a.planned>S.warnBefore){const w=endMs-S.warnBefore*60000;if(base+w>now+1000)list.push({id:9001,channelId:CH,title:'Faltam '+S.warnBefore+' min',body:a.name+': vá encerrando com calma.',schedule:{at:at(w),allowWhileIdle:true}})}
 if(base+endMs>now+1000)list.push({id:9002,channelId:CH,title:'Tempo previsto terminou',body:a.name+'. Abra o app para concluir ou pegar mais 5 min.',schedule:{at:at(endMs),allowWhileIdle:true}});
 if(a.split){let acc=0;a.split.forEach((s,i)=>{if(i>0&&base+acc*60000>now+1000)list.push({id:9010+i,channelId:CH,title:'Agora: '+s.label,body:a.name+' · '+s.min+' min',schedule:{at:at(acc*60000),allowWhileIdle:true}});acc+=s.min})}
 try{if(list.length)await LN.schedule({notifications:list})}catch(e){console.warn(e)}}
'''
rep("/* ---------- toast ---------- */",NATIVE+"\n/* ---------- toast ---------- */")

# som/vibração no app só quando o Android não estiver avisando
rep("function chime(kind){if(!S.sound","function chime(kind){if(nativeOK()&&document.visibilityState!=='visible')return;if(!S.sound")
rep("if(!a.warned&&S.warnBefore>0&&r<=S.warnBefore*60&&r>0&&a.planned>S.warnBefore){a.warned=true;save();chime('warn');buzz();",
    "if(!a.warned&&S.warnBefore>0&&r<=S.warnBefore*60&&r>0&&a.planned>S.warnBefore){a.warned=true;save();if(!nativeOK()){chime('warn');buzz()}")
rep("if(!a.ended&&r<=0){a.ended=true;save();chime('end');buzz();sysNotify('Tempo previsto terminou',a.name);",
    "if(!a.ended&&r<=0){a.ended=true;save();if(!nativeOK()){chime('end');buzz();sysNotify('Tempo previsto terminou',a.name)}")
rep("if(cur!==a.seg){a.seg=cur;save();chime('warn');buzz();","if(cur!==a.seg){a.seg=cur;save();if(!nativeOK()){chime('warn');buzz()}")
rep("if(n.min>=st&&n.min<st+3){day.fired[t.id]=1;save();chime('warn');buzz();sysNotify(RMSG[t.remind],t.name);",
    "if(n.min>=st&&n.min<st+3){day.fired[t.id]=1;save();if(!nativeOK()){chime('warn');buzz();sysNotify(RMSG[t.remind],t.name)}")

# cronômetro: reagendar avisos nativos em cada mudança
rep("S.active=Object.assign({startedAt:Date.now(),pausedAt:null,pausedTotal:0,warned:false,ended:false,seg:0,checked:[]},opts);save();openFocus();wakeOn()}",
    "S.active=Object.assign({startedAt:Date.now(),pausedAt:null,pausedTotal:0,warned:false,ended:false,seg:0,checked:[]},opts);save();openFocus();wakeOn();syncTimerNotifs()}")
rep("const kind=a.kind,taskId=a.taskId,date=a.date;S.active=null;save();wakeOff();","const kind=a.kind,taskId=a.taskId,date=a.date;S.active=null;save();wakeOff();syncTimerNotifs();")
rep("pause:()=>{S.active.pausedAt=Date.now();save();updateFocus(true)},","pause:()=>{S.active.pausedAt=Date.now();save();updateFocus(true);syncTimerNotifs()},")
rep("a.pausedAt=null;save();updateFocus(true);wakeOn()},","a.pausedAt=null;save();updateFocus(true);wakeOn();syncTimerNotifs()},")
rep("save();renderFocus();toast('Mais 5 minutos.')},","save();renderFocus();syncTimerNotifs();toast('Mais 5 minutos.')},")
rep("cancelTimer:()=>{S.active=null;save();wakeOff();closeFocus()},","cancelTimer:()=>{S.active=null;save();wakeOff();syncTimerNotifs();closeFocus()},")
rep("S.active=null;wakeOff();$('#focus').hidden=true;document.body.style.overflow=''}\n  save();closeModal();",
    "S.active=null;wakeOff();syncTimerNotifs();$('#focus').hidden=true;document.body.style.overflow=''}\n  save();closeModal();")

# lembretes semanais: reagendar quando horários/lembretes mudam
rep("S[draft.tab]=v.sorted;refreshTodayPlan(draft.tab);draft=null;save();","S[draft.tab]=v.sorted;refreshTodayPlan(draft.tab);draft=null;save();syncNativeReminders();")
rep("S.split=clone(DEF_SPLIT);draft=null;save();","S.split=clone(DEF_SPLIT);draft=null;save();syncNativeReminders();")
rep("else if(act==='notif'){S.notif[d.k]=el.checked;save();","else if(act==='notif'){S.notif[d.k]=el.checked;save();syncNativeReminders();")
rep("save();view='home';render();toast('Pronto! Comece pela próxima etapa.')}","save();view='home';render();toast('Pronto! Comece pela próxima etapa.');nativeInit(true)}")
rep("try{localStorage.removeItem(KEY)}catch(e){}","try{localStorage.removeItem(KEY)}catch(e){}cancelRange(1000,9099);")
rep("else if(act==='warn'){S.warnBefore=+el.value;save();","else if(act==='warn'){S.warnBefore=+el.value;save();syncTimerNotifs();")

# textos de Ajustes e onboarding
rep(" const perm=!('Notification'in window)?'unsupported':Notification.permission;",
    " const perm=!('Notification'in window)?'unsupported':Notification.permission;\n if(LN){h+=`<section class=\"card\"><span class=\"label\">Lembretes</span>${N.map(([id,l])=>`<label class=\"switch\"><span>${l}</span><input type=\"checkbox\" data-act-change=\"notif\" data-k=\"${id}\" ${S.notif[id]?'checked':''}></label>`).join('')}<div class=\"banner info\"><span>${nativePerm==='granted'?'<b>Avisos ativos.</b> Chegam mesmo com o app fechado ou a tela bloqueada, inclusive o fim de cada etapa do cronômetro.':'<b>Os avisos estão desligados.</b> Toque abaixo para permitir. Se não abrir a pergunta, vá em Configurações do Android → Apps → Rotina do Gabriel → Notificações.'} Se algum aviso atrasar ou não chegar, desative a economia de bateria para este app.</span>${nativePerm!=='granted'?'<div><button class=\"btn sm\" data-act=\"askNative\">Permitir avisos</button></div>':''}</div></section>`}else{")
rep("Para ser avisado com o celular bloqueado, crie alarmes no relógio do Android nos mesmos horários.</span>${perm==='default'?'<div><button class=\"btn sm\" data-act=\"askNotif\">Permitir notificações</button></div>':''}</div></section>`;",
    "Para ser avisado com o celular bloqueado, crie alarmes no relógio do Android nos mesmos horários.</span>${perm==='default'?'<div><button class=\"btn sm\" data-act=\"askNotif\">Permitir notificações</button></div>':''}</div></section>`;}")
rep("<p class=\"small muted\">Os dados ficam salvos só neste aparelho. Os lembretes aparecem com o app aberto.</p>",
    "<p class=\"small muted\">Os dados ficam salvos só neste aparelho. ${LN?'Na próxima tela, permita as notificações para receber os avisos com o app fechado.':'Os lembretes aparecem com o app aberto.'}</p>")
rep("Tudo fica salvo só neste navegador, neste aparelho. Se limpar os dados do navegador ou trocar de celular",
    "Tudo fica salvo só neste aparelho. Se desinstalar o app, limpar os dados dele ou trocar de celular")
rep(" askNotif:async()=>"," askNative:async()=>{await nativeInit(true);render();toast(nativePerm==='granted'?'Avisos ativados.':'Permita em Configurações do Android → Apps → Rotina do Gabriel.')},\n askNotif:async()=>")
rep("load();lastKey=today();render();if(S.active&&S.setupDone)openFocus();",
    "load();lastKey=today();render();if(S.active&&S.setupDone)openFocus();\nif(LN&&S.setupDone)nativeInit(false).then(()=>{if(view==='ajustes')render()});\nif(NATIVE)document.addEventListener('resume',()=>{render();syncTimerNotifs()});")
out=out.rstrip()+'\n</body>\n</html>\n'
open(sys.argv[2],'w').write(out)
print('ok',len(out))
