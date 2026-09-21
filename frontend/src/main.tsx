
import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

const API="http://localhost:8000/api";
type E={market:string,expert:string,timestamp:string,quote:string,source:string};
function Evidence({e}:{e:E}){return <div className="evidence"><div><b>{e.market}</b><span>{e.timestamp}</span></div><blockquote>“{e.quote}”</blockquote><small>{e.expert} · {e.source}</small></div>}
function App(){
 const [qs,setQs]=useState<any[]>([]),[id,setId]=useState(3),[tab,setTab]=useState("guide"),[res,setRes]=useState<any>(),[themes,setThemes]=useState<any>(),[q,setQ]=useState(""),[chat,setChat]=useState<any>();
 useEffect(()=>{fetch(API+"/guide/questions").then(r=>r.json()).then(setQs)},[]);
 useEffect(()=>{if(tab==="guide")fetch(API+"/guide/answer",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question_id:id})}).then(r=>r.json()).then(setRes)},[id,tab]);
 const loadThemes=()=>{setTab("themes");fetch(API+"/themes",{method:"POST"}).then(r=>r.json()).then(setThemes)};
 const ask=()=>fetch(API+"/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question:q})}).then(r=>r.json()).then(setChat);
 return <><header><div><strong>ExpertCall AI</strong><small>Evidence-grounded expert interview analysis</small></div><label>3 experts · 3 markets</label></header>
 <nav><button className={tab==="guide"?"on":""} onClick={()=>setTab("guide")}>Interview Guide</button><button className={tab==="themes"?"on":""} onClick={loadThemes}>Themes & Differences</button><button className={tab==="ask"?"on":""} onClick={()=>setTab("ask")}>Ask Across Calls</button></nav>
 {tab==="guide"&&<div className="layout"><aside><h3>Interview guide</h3>{qs.map(x=><button className={x.id===id?"sel":""} onClick={()=>setId(x.id)}>{x.id}. {x.question}</button>)}</aside><main>{res&&<><small className="eyebrow">GROUNDED ANSWER</small><h1>{res.question}</h1><p className="summary">{res.answer}</p><div className="evidenceGrid">{res.evidence.map((e:E)=><div className="card"><h2>{e.market}</h2><Evidence e={e}/></div>)}</div></>}</main></div>}
 {tab==="themes"&&<main className="wide"><small className="eyebrow">CROSS-CALL ANALYSIS</small><h1>Themes & areas of differing emphasis</h1>{themes&&<><h2>Common themes</h2>{themes.common_themes.map((x:string)=><div className="row">{x}</div>)}<h2>Areas of differing emphasis</h2>{themes.differing_emphasis.map((x:string)=><div className="row">{x}</div>)}</>}</main>}
 {tab==="ask"&&<main className="wide"><small className="eyebrow">RESEARCH ASSISTANT</small><h1>Ask across all transcripts</h1><div className="input"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="e.g. How do purchasing timelines differ across markets?" onKeyDown={e=>e.key==="Enter"&&ask()}/><button onClick={ask}>Ask</button></div>{chat&&<><p className="summary">{chat.answer}</p>{chat.evidence.map((e:E)=><Evidence e={e}/>)}</>}</main>}
 <footer>Evidence is retrieved from the supplied transcripts; quotes and timestamps are source metadata.</footer></>
}
createRoot(document.getElementById("root")!).render(<App/>);
