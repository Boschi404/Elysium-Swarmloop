"""Elysium-Bench LUNGO — SENZA timeout (max 600s)
5 categorie × 4 loop + Re-Test = 25 task
Skill: elysium-swarmloop — tempo illimitato per ogni task"""

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
HERMES_TIMEOUT = 600  # 10 min per task — niente timeout forzato
WEIGHTS = {"correctness": 40, "completeness": 25, "efficiency": 15, "robustness": 10, "clarity": 10}
SKILL_NAME = "elysium-swarmloop"

CATEGORIES = ["api_development","bug_fixing","algorithm_implementation","logical_deduction","code_review"]
TOTAL_LOOPS = 4

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
        return {"elapsed": round(time.time()-start,1), "files": [], "mode": f"timeout_{HERMES_TIMEOUT}s"}

def score_task(task_dir, workspace):
    try:
        return ScoringEngine(task_dir=task_dir, solution_dir=workspace/"workspace", weights=WEIGHTS).evaluate()
    except Exception as e:
        s = ScoreBreakdown(task_type="code")
        s.gaps.append(str(e))
        return s

def run_tests(workspace):
    ws = workspace / "workspace"; td = ws / "tests"
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

# ═══════════ MAIN ═══════════
print(f"""
┌───────────────────────────────────────────────────────────────┐
│ 🚀 LUNGO BENCHMARK — SENZA TIMEOUT (600s per task)          │
│ {len(CATEGORIES)} categorie × {TOTAL_LOOPS} loop + Re-Test = {len(CATEGORIES)*(TOTAL_LOOPS+1)} task  │
│ Skill: {SKILL_NAME} v0.7.2                                   │
│ Ogni task ha max {HERMES_TIMEOUT}s per completare             │
└───────────────────────────────────────────────────────────────┘
""")

cfg = {"categories":[{"id":c,"name":c,"description":"","weight":1.0} for c in CATEGORIES]}
registry = TaskRegistry(TASKS_DIR, cfg)
cats = registry.discover()

task_map = {}
for cat in cats:
    tasks = {}
    for t in cat.tasks:
        m = re.match(r"T(\d+)", t.id)
        if m: tasks[int(m.group(1))] = t
    task_map[cat.id] = tasks
    print(f"  📂 {cat.id}")

clean_ws()
all_results = {"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S"),"categories":CATEGORIES,
               "total_loops":TOTAL_LOOPS,"skill":f"{SKILL_NAME} v0.7.2 (no timeout)","loops":{}}
start_all = time.time()
total_tasks = 0
timeout_count = 0

for phase in range(1, TOTAL_LOOPS + 2):
    is_retest = phase == TOTAL_LOOPS + 1
    task_idx = 1 if is_retest else phase
    label = "LOOP 1 (measurement)" if phase == 1 else ("RE-TEST" if is_retest else f"LOOP {phase} (practice)")
    print(f"\n{'─'*60}")
    print(f"  📍 {label}")
    print(f"{'─'*60}")
    phase_scores = {}
    
    for cat_id in CATEGORIES:
        t = task_map[cat_id].get(task_idx)
        if not t: continue
        
        print(f"\n  {t.id}: {t.name} (type={t.task_type}, diff={t.difficulty})", end=" ", flush=True)
        
        ws = create_ws(t.task_dir, t.id, f"p{phase}")
        result = solve_task(t, ws)
        total_tasks += 1
        
        if "timeout" in result["mode"]:
            timeout_count += 1
            print(f"→ ⏰ TIMEOUT ({result['elapsed']}s)")
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
            ts_str = f"{tests['passed']}/{tests['total']}" if tests['total']>0 else "no-tests"
            print(f"→ {fmt(score.total)}/100 {'✅' if score.passed else '❌'} [{ts_str}] ⏱{result['elapsed']}s")
        
        sd["duration_s"] = result["elapsed"]
        sd["mode"] = result["mode"]
        phase_scores[t.id] = sd
        
        elapsed = time.time() - start_all
        done = total_tasks / (len(CATEGORIES)*(TOTAL_LOOPS+1))
        if done > 0:
            eta = (elapsed / done - elapsed) / 60
            print(f"     ⏳ {total_tasks}/{len(CATEGORIES)*(TOTAL_LOOPS+1)} | +{elapsed/60:.1f}min | ETA ~{eta:.0f}min")
    
    all_results["loops"]["retest" if is_retest else f"loop{phase}"] = phase_scores

# ─── REPORT ───
total_elapsed = time.time() - start_all
print(f"\n{'═'*60}")
print(f"  📊 FINAL REPORT — LUNGO (no timeout)")
print(f"{'═'*60}")

cats_data = {}
for cat_id in CATEGORIES:
    t1 = f"T01_{cat_id}"
    l1 = all_results["loops"]["loop1"].get(t1,{}).get("total",0)
    l2 = all_results["loops"]["loop2"].get(f"T02_{cat_id}",{}).get("total",0)
    l3 = all_results["loops"]["loop3"].get(f"T03_{cat_id}",{}).get("total",0)
    l4 = all_results["loops"]["loop4"].get(f"T04_{cat_id}",{}).get("total",0)
    rt = all_results["loops"]["retest"].get(t1,{}).get("total",0)
    cats_data[cat_id] = {"l1":l1,"l2":l2,"l3":l3,"l4":l4,"rt":rt,"delta":rt-l1}

print(f"\n  {'Categoria':<30} {'L1':<8} {'L2':<8} {'L3':<8} {'L4':<8} {'Re-Test':<10} {'Δ':<8}")
print(f"  {'─'*75}")
for cat_id, cd in cats_data.items():
    d = cd['delta']; di = "📈" if d > 0 else ("📉" if d < 0 else "➡️")
    print(f"  {cat_id:<30} {cd['l1']:<8.1f} {cd['l2']:<8.1f} {cd['l3']:<8.1f} {cd['l4']:<8.1f} {cd['rt']:<10.1f} {d:>+6.1f} {di}")

l1_avg = sum(cd["l1"] for cd in cats_data.values())/len(cats_data)
rt_avg = sum(cd["rt"] for cd in cats_data.values())/len(cats_data)
delta_avg = rt_avg - l1_avg

print(f"\n  {'─'*75}")
print(f"  {'MEDIA':<30} {l1_avg:<8.1f} {'':<8} {'':<8} {'':<8} {rt_avg:<10.1f} {delta_avg:>+6.1f}")
print(f"  {'Improvement':<30} {'✅ YES' if delta_avg >= 5 else '❌ NO'} ({delta_avg:+.1f})")
print(f"  {'Timeout totali':<30} {timeout_count}/{total_tasks}")
print(f"  {'Durata':<30} {total_elapsed/60:.1f} min")

report = {"benchmark":"Elysium-Bench LUNGO (no timeout)","version":"1.0.0",
          "skill":f"{SKILL_NAME} v0.7.2 (no timeout)","categories":CATEGORIES,
          "total_loops":TOTAL_LOOPS,"total_tasks":total_tasks,"timeouts":timeout_count,
          "per_category":cats_data,"avg_loop1":round(l1_avg,1),"avg_retest":round(rt_avg,1),
          "avg_delta":round(delta_avg,1),"improvement_detected":delta_avg>=5,
          "duration_minutes":round(total_elapsed/60,1),"loops":all_results["loops"]}

RISULTATI_DIR.mkdir(parents=True, exist_ok=True)
ts = time.strftime("%Y%m%d_%H%M%S")
basename = f"lungo_notimeout_v072_{ts}"
jp = RISULTATI_DIR / f"{basename}.json"
jp.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

md = [
    f"# LUNGO (no timeout) — Elysium Swarmloop v0.7.2",
    f"**Durata:** {total_elapsed/60:.1f} min | **Task:** {total_tasks} | **Timeout:** {timeout_count}",
    f"**Ogni task aveva max {HERMES_TIMEOUT}s — nessun timeout forzato.**",
    f"", f"## 📊 Progressione",
    f"| Categoria | L1 | L2 | L3 | L4 | Re-Test | Δ |",
    f"|---|:---:|:---:|:---:|:---:|:---:|:---:|",
]
for cat_id, cd in cats_data.items():
    d = cd['delta']; di = "📈" if d > 5 else ("📉" if d < -5 else "➡️")
    md.append(f"| {cat_id} | {cd['l1']:.1f} | {cd['l2']:.1f} | {cd['l3']:.1f} | {cd['l4']:.1f} | {cd['rt']:.1f} | {d:+.1f} {di} |")
md += [
    f"", f"**Loop 1 Avg:** {l1_avg:.1f} | **Re-Test Avg:** {rt_avg:.1f} | **Δ:** {delta_avg:+.1f}",
    f"**Miglioramento:** {'✅ SI' if delta_avg >= 5 else '❌ NO'} ({delta_avg:+.1f})",
    f"**Timeout:** {timeout_count}/{total_tasks} task",
    f"", f"## ⏱ Dettaglio Task",
    f"| Phase | Task | Type | Score | Tests | Durata | Mode |",
    f"|-------|------|:---:|:----:|:-----:|:------:|:----:|",
]
for pk in ['loop1','loop2','loop3','loop4','retest']:
    scores = all_results["loops"].get(pk, {})
    for tid, sd in sorted(scores.items()):
        t = sd['tests']; ts = f"{t['passed']}/{t['total']}" if t['total']>0 else "no-tests"
        md.append(f"| {pk} | {tid} | {sd.get('task_type','?')} | {sd['total']:.1f} | {ts} | {sd['duration_s']}s | {sd['mode']} |")

mp = RISULTATI_DIR / f"{basename}.md"
mp.write_text("\n".join(md), encoding="utf-8")
print(f"\n  📁 {basename}.json / .md")

clean_ws()
print(f"\n  ✅ LUNGO (no timeout) completato!\n")
