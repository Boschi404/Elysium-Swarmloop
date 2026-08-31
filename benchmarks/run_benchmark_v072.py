"""Elysium-Bench v0.7.2 — Quick + Medium + Lungo CON skill aggiornata
Usa elysium-swarmloop v0.7.2 (la skill appena caricata)."""

import json, re, shutil, subprocess, sys, time, textwrap
from pathlib import Path

BENCH_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BENCH_DIR))
sys.path.insert(0, str(Path.home() / "Elysium-Bench"))

from elysium_bench.scoring import ScoringEngine, ScoreBreakdown
from elysium_bench.task_registry import TaskRegistry

RISULTATI_DIR = BENCH_DIR / "risultati"
TASKS_DIR = Path.home() / "Elysium-Bench" / "tasks"
WORKSPACES_DIR = BENCH_DIR / "workspaces"
HERMES_TIMEOUT = 180
WEIGHTS = {"correctness": 40, "completeness": 25, "efficiency": 15, "robustness": 10, "clarity": 10}
SKILL_NAME = "elysium-swarmloop"
TAG = "v072"

def fmt(v): return f"{v:.1f}"

def clean_ws():
    if WORKSPACES_DIR.exists(): shutil.rmtree(WORKSPACES_DIR)
    WORKSPACES_DIR.mkdir(parents=True)

def create_ws(task_dir, task_id, tag):
    ws = WORKSPACES_DIR / f"{task_id}_{tag}"
    if ws.exists(): shutil.rmtree(ws)
    ws.mkdir(parents=True); (ws / "workspace").mkdir()
    for sd in ["tests", "repo"]:
        src = task_dir / sd
        if src.exists():
            dst = ws / "workspace" / sd
            if sd == "repo":
                for f in src.iterdir(): shutil.copy2(f, ws / "workspace")
            else:
                shutil.copytree(src, dst, dirs_exist_ok=True)
    return ws

def solve_task(task, workspace):
    ws_path = workspace / "workspace"
    prompt = textwrap.dedent(f"""\
    TASK: {task.id} - {task.name}
    DESCRIPTION: {task.description}
    WORKSPACE: {ws_path}
    INSTRUCTIONS:
    1. Solve this task completely
    2. Write ALL solution files to {ws_path}/
    3. Ensure tests in {ws_path / 'tests'}/ pass (if they exist)
    4. Return a brief summary
    SKILL: {SKILL_NAME}""")
    start = time.time()
    try:
        r = subprocess.run(["hermes","chat","-q",prompt,"--skills",SKILL_NAME,"-Q"],
                          capture_output=True, text=True, timeout=HERMES_TIMEOUT)
        elapsed = time.time() - start
        files = sorted(f.relative_to(ws_path).as_posix() for f in ws_path.rglob("*") if f.is_file())
        return {"elapsed": round(elapsed, 1), "files": files, "mode": "elysium"}
    except subprocess.TimeoutExpired:
        return {"elapsed": round(time.time()-start,1), "files": [], "mode": "timeout"}

def score_task(task_dir, workspace):
    try:
        return ScoringEngine(task_dir=task_dir, solution_dir=workspace/"workspace", weights=WEIGHTS).evaluate()
    except Exception as e:
        s = ScoreBreakdown(task_type="code")
        s.gaps.append(str(e))
        return s

def run_tests(workspace):
    ws = workspace / "workspace"
    td = ws / "tests"
    if not td.exists(): return {"passed":0,"total":0,"output":"No tests dir"}
    try:
        r = subprocess.run([sys.executable,"-m","pytest",str(td),"-q","--tb=short"],
                          capture_output=True,text=True,timeout=60,cwd=str(ws))
        mp = re.search(r"(\d+)\s+passed", r.stdout)
        mf = re.search(r"(\d+)\s+failed", r.stdout)
        passed = int(mp.group(1)) if mp else 0
        failed = int(mf.group(1)) if mf else 0
        if r.returncode == 0 and mp: passed = int(mp.group(1)); failed = 0
        return {"passed":passed,"total":passed+failed,"output":r.stdout}
    except: return {"passed":0,"total":0,"output":"Test error"}

def run_benchmark(name, categories, total_loops):
    print(f"\n{'═'*60}")
    print(f"  🏁 {name} (Elysium {TAG})")
    print(f"{'═'*60}")
    
    cfg = {"categories":[{"id":c,"name":c,"description":"","weight":1.0} for c in categories]}
    registry = TaskRegistry(TASKS_DIR, cfg)
    cats = registry.discover()
    task_map = {}
    for cat in cats:
        tasks = {}
        for t in cat.tasks:
            m = re.match(r"T(\d+)", t.id)
            if m: tasks[int(m.group(1))] = t
        task_map[cat.id] = tasks
    
    clean_ws()
    all_results = {"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S"),"categories":categories,
                   "total_loops":total_loops,"skill":f"{SKILL_NAME} {TAG}","loops":{}}
    start_time = time.time()
    
    for phase in range(1, total_loops + 2):
        is_retest = phase == total_loops + 1
        task_idx = 1 if is_retest else phase
        label = "LOOP 1 (measurement)" if phase == 1 else ("RE-TEST" if is_retest else f"LOOP {phase} (practice)")
        print(f"\n  📍 {label}")
        phase_scores = {}
        for cat_id in categories:
            t = task_map[cat_id].get(task_idx)
            if not t: continue
            print(f"    {t.id}: {t.name}...", end=" ", flush=True)
            ws = create_ws(t.task_dir, t.id, f"p{phase}")
            result = solve_task(t, ws)
            if result["mode"] == "timeout":
                print(f"⏰ TIMEOUT")
                sd = {"correctness":0,"completeness":0,"efficiency":0,"robustness":0,"clarity":0,
                      "total":0,"passed":False,"task_type":t.task_type,"gaps":["Timeout"],
                      "tests":{"passed":0,"total":0,"output":"Timeout"},"files":[],"mode":"timeout"}
            else:
                score = score_task(t.task_dir, ws)
                tests = run_tests(ws)
                sd = score.to_dict()
                sd["total"] = round(score.total, 1)
                sd["tests"] = tests
                sd["files"] = result["files"]
                icon = "✅" if score.passed else "❌"
                ts = f"{tests['passed']}/{tests['total']}" if tests['total']>0 else "no-tests"
                print(f"{fmt(score.total)}/100 {icon} [{ts}] ⏱{result['elapsed']}s")
            sd["duration_s"] = result["elapsed"]
            sd["mode"] = result["mode"]
            phase_scores[t.id] = sd
        
        all_results["loops"]["retest" if is_retest else f"loop{phase}"] = phase_scores
    
    total_elapsed = time.time() - start_time
    cats_data = {}
    for cat_id in categories:
        t1 = f"T01_{cat_id}"
        l1 = all_results["loops"]["loop1"].get(t1,{}).get("total",0)
        rt = all_results["loops"]["retest"].get(t1,{}).get("total",0)
        cats_data[cat_id] = {"loop1": l1, "retest": rt, "delta": rt-l1}
    
    l1_avg = sum(cd["loop1"] for cd in cats_data.values())/max(len(cats_data),1)
    rt_avg = sum(cd["retest"] for cd in cats_data.values())/max(len(cats_data),1)
    print(f"\n  📊 Loop 1: {l1_avg:.1f} | Re-Test: {rt_avg:.1f} | Δ: {rt_avg-l1_avg:+.1f} | ⏱{total_elapsed/60:.1f}min")
    
    report = {"benchmark":f"{name} (Elysium {TAG})","skill":f"{SKILL_NAME} {TAG}",
              "version":TAG,"categories":categories,"total_loops":total_loops,
              "per_category":cats_data,"avg_loop1":round(l1_avg,1),
              "avg_retest":round(rt_avg,1),"avg_delta":round(rt_avg-l1_avg,1),
              "duration_minutes":round(total_elapsed/60,1),"loops":all_results["loops"]}
    
    RISULTATI_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    slug = name.lower().replace(" ","_")
    basename = f"{slug}_{TAG}_{ts}"
    jp = RISULTATI_DIR / f"{basename}.json"
    jp.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    
    md = [
        f"# {name} (Elysium Swarmloop v{TAG})",
        f"**Durata:** {total_elapsed/60:.1f} min | **Skill:** {SKILL_NAME} v{TAG}",
        f"**Categorie:** {', '.join(categories)} | **Task:** {sum(len(v) for v in all_results['loops'].values())}",
        f"", f"| Categoria | Loop 1 | Re-Test | Δ |", f"|---|---|---:|:---:|",
    ]
    for cid, cd in cats_data.items():
        md.append(f"| {cid} | {cd['loop1']:.1f} | {cd['retest']:.1f} | {cd['delta']:+.1f} |")
    md.append(f"\n**Loop 1 Avg:** {l1_avg:.1f} | **Re-Test Avg:** {rt_avg:.1f} | **Δ:** {rt_avg-l1_avg:+.1f}")
    md.append(f"\n## Dettaglio Task\n| Phase | Task | Score | Tests | Durata |")
    md.append(f"|-------|------|:----:|:-----:|:------:|")
    for pk, scores in all_results["loops"].items():
        for tid, sd in scores.items():
            t = sd["tests"]
            ts = f"{t['passed']}/{t['total']}" if t['total']>0 else "no-tests"
            md.append(f"| {pk} | {tid} | {sd['total']:.1f} | {ts} | {sd['duration_s']}s |")
    mp = RISULTATI_DIR / f"{basename}.md"
    mp.write_text("\n".join(md), encoding="utf-8")
    print(f"    📁 {jp.name}")
    clean_ws()
    return report

# ═══════════ MAIN ═══════════
print("\n" + "┌" + "─"*61 + "┐")
print("│ 🚀 BENCHMARK CON ELYSIUM SWARMLOOP v0.7.2               │")
print("│ Quick + Medium + Lungo in serie                          │")
print("└" + "─"*61 + "┘")

start = time.time()

print("\n🔍 Skill attuale:", SKILL_NAME)
import subprocess as sp
r = sp.run(["hermes","chat","-q","Quale versione di elysium-swarmloop stai usando? Rispondi solo con la versione.","--skills",SKILL_NAME,"-Q"],
          capture_output=True, text=True, timeout=60)
print(f"   Risposta: {r.stdout.strip()[-50:]}")
print(f"   (se v0.7.2 → skill aggiornata correttamente)")

print(f"\n{'='*60}")
print(f"  AVVIO QUICK BENCHMARK (1 cat × 2 loop)")
print(f"{'='*60}")
r1 = run_benchmark("Quick", ["api_development"], 2)

print(f"\n{'='*60}")
print(f"  AVVIO MEDIUM BENCHMARK (4 cat × 3 loop)")
print(f"{'='*60}")
r2 = run_benchmark("Medium", ["api_development","bug_fixing","algorithm_implementation","data_analysis"], 3)

print(f"\n{'='*60}")
print(f"  AVVIO LUNGO BENCHMARK (5 cat × 4 loop)")
print(f"{'='*60}")
r3 = run_benchmark("Lungo", ["api_development","bug_fixing","algorithm_implementation","logical_deduction","code_review"], 4)

# Report finale
total = time.time() - start
print(f"\n{'═'*60}")
print(f"  📊 RIEPILOGO BENCHMARK Elysium Swarmloop v0.7.2")
print(f"{'═'*60}")
print(f"\n  {'Benchmark':<12} {'Loop 1':<10} {'Re-Test':<10} {'Δ':<10} {'Durata':<10}")
print(f"  {'─'*50}")
for name, rd in [("Quick",r1),("Medium",r2),("Lungo",r3)]:
    print(f"  {name:<12} {rd['avg_loop1']:<10.1f} {rd['avg_retest']:<10.1f} {rd['avg_delta']:<+10.1f} {rd['duration_minutes']:<10.1f}min")
print(f"\n  ⏱  Totale: {total/60:.1f} min")
print(f"  ✅ Benchmark v0.7.2 completati! File in risultati/\n")
