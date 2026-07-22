from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse, Response

from . import __version__
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook
from .core import AuthTwinEngine

HTML = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>AuthTwin</title><style>body{font-family:system-ui;margin:0;background:#0b1020;color:#e8edf7}header{padding:18px 24px;border-bottom:1px solid #26314d;display:flex;justify-content:space-between;gap:16px}main{padding:24px;display:grid;gap:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.card{background:#121a2d;border:1px solid #26314d;border-radius:12px;padding:18px}.muted{color:#9eabc5}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;border-bottom:1px solid #26314d;padding:10px;white-space:nowrap}.scroll{overflow:auto}.pill{padding:3px 7px;border:1px solid #3c4b70;border-radius:999px;font-size:12px}button,input{background:#0d1426;color:#e8edf7;border:1px solid #3c4b70;border-radius:8px;padding:8px}.drawer{position:fixed;right:0;top:0;height:100%;width:min(480px,90vw);background:#0f1729;border-left:1px solid #26314d;padding:20px;display:none;overflow:auto}.drawer.open{display:block}</style></head><body><header><b>AuthTwin</b><span>imr :: v__VERSION__</span><span id='jobStatus' class='muted'>Jobs: idle</span></header><main><div><input id='search' placeholder='Search matrix/resource/actor'><button id='searchBtn'>Search</button></div><div class='grid'><div class='card'><div class='muted'>Actors</div><h2 id='actors'>—</h2></div><div class='card'><div class='muted'>Resources</div><h2 id='resources'>—</h2></div><div class='card'><div class='muted'>Coverage</div><h2 id='coverage'>—</h2></div><div class='card'><div class='muted'>Findings</div><h2 id='findings'>—</h2></div></div><div class='card'><h3>Authorization Matrix</h3><p class='muted'>Unobserved cells remain <span class='pill'>UNKNOWN</span>; they are never findings by themselves.</p><div class='scroll'><table><thead id='head'></thead><tbody id='body'></tbody></table></div></div><div class='card'><h3>Counterfactual Plans</h3><div id='counterfactuals' class='muted'></div></div></main><aside id='drawer' class='drawer'><button id='closeDrawer'>Close</button><h3>Evidence / Explainability</h3><pre id='drawerBody'></pre></aside><script src='/assets/app.js'></script></body></html>"""
JS = """function esc(v){return String(v).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}async function load(){const s=await fetch('/api/summary').then(r=>r.json());for(const k of ['actors','resources','findings'])document.getElementById(k).textContent=s[k];document.getElementById('coverage').textContent=Math.round(s.coverage*100)+'%';const m=await fetch('/api/matrix').then(r=>r.json());document.getElementById('head').innerHTML='<tr><th>Resource</th><th>Operation</th>'+m.actors.map(a=>'<th>'+esc(a)+'</th>').join('')+'</tr>';document.getElementById('body').innerHTML=m.rows.map(row=>'<tr data-row=\''+encodeURIComponent(JSON.stringify(row))+'\'><td>'+esc(row.resource_id)+'</td><td>'+esc(row.operation)+'</td>'+m.actors.map(a=>'<td>'+esc(row.decisions[a]||'UNKNOWN')+'</td>').join('')+'</tr>').join('');document.querySelectorAll('tr[data-row]').forEach(r=>r.onclick=()=>openDrawer(JSON.parse(decodeURIComponent(r.dataset.row))));const c=await fetch('/api/counterfactuals').then(r=>r.json());document.getElementById('counterfactuals').innerHTML=c.slice(0,20).map(x=>'<div>'+esc(x.source_actor_id)+' → '+esc(x.candidate_actor_id)+' · '+esc(x.operation)+' · '+esc(x.resource_id)+' · '+esc(x.status)+'</div>').join('')||'No plans generated yet.'}function openDrawer(v){document.getElementById('drawerBody').textContent=JSON.stringify(v,null,2);document.getElementById('drawer').classList.add('open')}document.getElementById('closeDrawer').onclick=()=>document.getElementById('drawer').classList.remove('open');document.getElementById('searchBtn').onclick=()=>{const q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('#body tr').forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?'':'none')};document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();document.getElementById('search').focus()}});const jobStatus=document.getElementById('jobStatus');try{const events=new EventSource('/api/jobs/events');events.addEventListener('job',e=>{try{const j=JSON.parse(e.data);jobStatus.textContent='Job: '+(j.event_type||'event')+' · '+(j.job_id||'');}catch(_){}});events.onerror=()=>{jobStatus.textContent='Jobs: reconnecting';};}catch(_){jobStatus.textContent='Jobs: unavailable';}load().catch(()=>{});"""


def create_app(workspace: Path) -> FastAPI:
    app = FastAPI(title="AuthTwin Local API", version=__version__, docs_url="/docs", redoc_url=None)
    engine = AuthTwinEngine(workspace)
    shared_graph = TemporalGraph(workspace)
    shared_jobs = JobEngine(workspace)
    shared_lineage = EvidenceLineage(workspace)
    shared_notebook = ResearchNotebook(workspace)

    @app.middleware("http")
    async def headers(request: Any, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return HTML.replace("__VERSION__", __version__)

    @app.get("/assets/app.js")
    async def js() -> Response:
        return Response(JS, media_type="application/javascript")

    @app.get("/api/summary")
    async def summary() -> dict[str, object]:
        data = engine.store.load()
        coverage = engine.coverage()
        return {
            "version": __version__,
            "actors": len(data["actors"]),
            "resources": len(data["resources"]),
            "observations": len(data["observations"]),
            "findings": len(data["findings"]),
            "coverage": coverage.coverage,
        }

    @app.get("/api/state-machine")
    async def state_machine() -> dict[str, list[dict[str, Any]]]:
        return engine.state_machine()

    @app.get("/api/matrix")
    async def matrix() -> dict[str, Any]:
        return engine.matrix()

    @app.get("/api/coverage")
    async def coverage() -> dict[str, Any]:
        return engine.coverage().model_dump(mode="json")

    @app.get("/api/counterfactuals")
    async def counterfactuals() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in engine.counterfactuals()]

    @app.get("/api/graphql")
    async def graphql_surface() -> list[dict[str, Any]]:
        return engine.graphql_surface()

    @app.get("/api/batch")
    async def batch_surface() -> list[dict[str, Any]]:
        return engine.batch_authorization()


    @app.get("/api/search")
    async def shared_search(q: str, limit: int = 50) -> list[dict[str, Any]]:
        return shared_graph.search(q, max(1, min(limit, 500)))

    @app.get("/api/jobs")
    async def shared_jobs_endpoint() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_jobs.list()]

    @app.get("/api/jobs/events")
    async def shared_job_events(cursor: int = 0, once: bool = False) -> StreamingResponse:
        async def stream() -> Any:
            current = max(0, cursor)
            while True:
                events = shared_jobs.all_events(current)
                for event in events:
                    payload = json.dumps(event.model_dump(mode="json"), default=str)
                    yield f"id: {current}\nevent: job\ndata: {payload}\n\n"
                    current += 1
                if once:
                    if not events:
                        yield "event: heartbeat\ndata: {}\n\n"
                    break
                await asyncio.sleep(1.0)
        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

    @app.get("/api/notebook")
    async def shared_notebook_endpoint() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_notebook.list()]

    @app.get("/api/evidence-lineage/{artifact_id:path}")
    async def shared_lineage_endpoint(artifact_id: str) -> dict[str, Any]:
        try:
            return shared_lineage.explain(artifact_id)
        except KeyError:
            return {"artifact_id": artifact_id, "status": "UNKNOWN", "message": "No lineage record found."}

    return app
