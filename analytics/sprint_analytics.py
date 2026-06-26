#!/usr/bin/env python3
"""
SentiVision Sprint Analytics
- Cycle Time (이슈 오픈 → 클로즈 기간)
- Velocity (스프린트당 완료 이슈 수 / 스토리 포인트)
- Burndown Chart (스프린트 잔여 작업)

GitHub API로 실제 이슈 데이터를 수집하고,
아직 close되지 않은 이슈는 스프린트 계획 기준 시뮬레이션 포함.
"""
import subprocess
import json
import os
from datetime import datetime, timedelta, timezone

import matplotlib
matplotlib.use("Agg")  # 헤드리스 환경 대응
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

OWNER = "acertainromance401"
REPO = "SentiVision"
OUTPUT_DIR = "/Users/acertainromance401/Desktop/SentiVision/analytics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. GitHub API로 이슈 데이터 수집 ─────────────────────────────
def fetch_issues():
    result = subprocess.run(
        ["gh", "api", f"repos/{OWNER}/{REPO}/issues",
         "--method", "GET",
         "-f", "state=all",
         "-f", "per_page=50",
         "--paginate"],
        capture_output=True, text=True
    )
    raw = result.stdout.strip()
    # --paginate 출력은 JSON 배열이 연속될 수 있으므로 합치기
    try:
        issues = json.loads(raw)
    except json.JSONDecodeError:
        # 여러 배열 합치기
        import re
        arrays = re.findall(r'\[.*?\]', raw, re.DOTALL)
        issues = []
        for a in arrays:
            try:
                issues.extend(json.loads(a))
            except Exception:
                pass
    # PR 제외, #10~#21만 선택
    return [i for i in issues
            if "pull_request" not in i
            and 10 <= i["number"] <= 21]

print("GitHub API에서 이슈 데이터 수집 중...")
issues = fetch_issues()
print(f"  수집된 이슈: {len(issues)}개")

# ── 2. 이슈 데이터 정리 ───────────────────────────────────────────
SPRINT1_ISSUES = {10, 11, 12, 13, 14}
SPRINT2_ISSUES = {15, 16, 17, 18, 19}
BACKLOG_ISSUES = {20, 21}

# 스프린트 일정 (2026년 기준)
SPRINT1_START = datetime(2026, 4, 27, tzinfo=timezone.utc)
SPRINT1_END   = datetime(2026, 5, 17, tzinfo=timezone.utc)
SPRINT2_START = datetime(2026, 5, 18, tzinfo=timezone.utc)
SPRINT2_END   = datetime(2026, 6, 7,  tzinfo=timezone.utc)

# 스토리 포인트 (라벨 기반 추정)
STORY_POINTS = {
    10: 8, 11: 5, 12: 8, 13: 5, 14: 3,   # Sprint 1
    15: 8, 16: 5, 17: 5, 18: 3, 19: 5,   # Sprint 2
    20: 3, 21: 8,                          # Backlog
}

rows = []
for issue in issues:
    num = issue["number"]
    created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
    closed = None
    if issue["closed_at"]:
        closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))

    labels = [l["name"] for l in issue["labels"]]
    sprint = 1 if num in SPRINT1_ISSUES else (2 if num in SPRINT2_ISSUES else 0)

    rows.append({
        "number": num,
        "title": issue["title"][:40],
        "sprint": sprint,
        "created_at": created,
        "closed_at": closed,
        "story_points": STORY_POINTS.get(num, 3),
        "labels": labels,
        "state": issue["state"],
    })

df = pd.DataFrame(rows).sort_values("number").reset_index(drop=True)

# ── 3. Cycle Time 계산 ────────────────────────────────────────────
# 실제 close된 이슈: 실제 Cycle Time
# open 이슈: 오늘까지의 진행 시간 (WIP age)
TODAY = datetime(2026, 4, 27, tzinfo=timezone.utc)

def cycle_time_days(row):
    if row["closed_at"]:
        return (row["closed_at"] - row["created_at"]).total_seconds() / 86400
    else:
        raw = (TODAY - row["created_at"]).total_seconds() / 86400
        return max(0.0, raw)

df["cycle_time_days"] = df.apply(cycle_time_days, axis=1)
df["is_closed"] = df["closed_at"].notna()

print("\n=== Cycle Time 분석 ===")
closed_df = df[df["is_closed"]]
if len(closed_df) > 0:
    print(f"완료된 이슈: {len(closed_df)}개")
    print(f"  평균 Cycle Time: {closed_df['cycle_time_days'].mean():.1f}일")
    print(f"  중앙값: {closed_df['cycle_time_days'].median():.1f}일")
else:
    print("완료된 이슈 없음 (모두 open 상태)")
    print(f"  현재 WIP Age 평균: {df['cycle_time_days'].mean():.1f}일")

# ── 4. Velocity 계산 ─────────────────────────────────────────────
print("\n=== Velocity 분석 ===")
s1 = df[df["sprint"] == 1]
s2 = df[df["sprint"] == 2]

s1_planned_pts  = s1["story_points"].sum()
s1_done_pts     = s1[s1["is_closed"]]["story_points"].sum()
s1_planned_cnt  = len(s1)
s1_done_cnt     = len(s1[s1["is_closed"]])

s2_planned_pts  = s2["story_points"].sum()
s2_done_pts     = s2[s2["is_closed"]]["story_points"].sum()
s2_planned_cnt  = len(s2)
s2_done_cnt     = len(s2[s2["is_closed"]])

print(f"Sprint 1: 계획 {s1_planned_pts}pts ({s1_planned_cnt}개) | 완료 {s1_done_pts}pts ({s1_done_cnt}개)")
print(f"Sprint 2: 계획 {s2_planned_pts}pts ({s2_planned_cnt}개) | 완료 {s2_done_pts}pts ({s2_done_cnt}개)")

# ── 5. 시각화 ─────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "AppleGothic",   # macOS 한글
    "axes.unicode_minus": False,
    "figure.dpi": 120,
})

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("SentiVision Sprint Analytics Dashboard", fontsize=16, fontweight="bold")

# ── 5a. 이슈 현황 / 스토리 포인트 분포 ──────────────────────────
ax1 = axes[0]

# 스프린트별 스토리 포인트 분포 (수평 스택 바)
sprint_labels = ["Sprint 1\n(#10-14)", "Sprint 2\n(#15-19)", "Backlog\n(#20-21)"]
sprints_data = [
    df[df["sprint"] == 1],
    df[df["sprint"] == 2],
    df[df["sprint"] == 0],
]

categories = ["feature", "bug", "test", "infra"]
cat_colors  = {"feature": "#42A5F5", "bug": "#EF5350", "test": "#66BB6A", "infra": "#AB47BC", "other": "#BDBDBD"}

left = np.zeros(3)
for cat in categories + ["other"]:
    vals = []
    for sdf in sprints_data:
        pts = 0
        for _, row in sdf.iterrows():
            if cat == "other":
                has = not any(c in row["labels"] for c in categories)
            else:
                has = any(cat in lbl for lbl in row["labels"])
            if has:
                pts += row["story_points"]
        vals.append(pts)
    vals = np.array(vals, dtype=float)
    if vals.sum() > 0:
        bars = ax1.barh(sprint_labels, vals, left=left, color=cat_colors[cat], label=cat.capitalize())
        left += vals

ax1.set_xlabel("Story Points")
ax1.set_title("스프린트별 Story Points 분포")
ax1.legend(fontsize=8, bbox_to_anchor=(1.0, 1.0), loc="upper left")
ax1.grid(axis="x", alpha=0.3)

# 총계 표시
for i, sdf in enumerate(sprints_data):
    total = sdf["story_points"].sum()
    ax1.text(total + 0.3, i, f"{total}pts", va="center", fontsize=9, fontweight="bold")

# ── 5b. Velocity 바 차트 ──────────────────────────────────────────
ax2 = axes[1]
sprints = ["Sprint 1", "Sprint 2"]
planned = [s1_planned_pts, s2_planned_pts]
done    = [s1_done_pts,    s2_done_pts]

x = np.arange(len(sprints))
width = 0.35
bars1 = ax2.bar(x - width/2, planned, width, label="계획 (Planned)", color="#90CAF9", edgecolor="#1565C0")
bars2 = ax2.bar(x + width/2, done,    width, label="완료 (Done)",    color="#A5D6A7", edgecolor="#2E7D32")

# 값 표시
for bar in bars1:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f"{int(bar.get_height())}pts", ha="center", va="bottom", fontsize=9)
for bar in bars2:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f"{int(bar.get_height())}pts", ha="center", va="bottom", fontsize=9)

ax2.set_xticks(x)
ax2.set_xticklabels(sprints)
ax2.set_ylabel("Story Points")
ax2.set_title("Velocity (스프린트별 계획 vs 완료)")
ax2.legend(fontsize=9)
ax2.grid(axis="y", alpha=0.3)

# 완료율 표시
for i, (p, d) in enumerate(zip(planned, done)):
    rate = (d / p * 100) if p > 0 else 0
    ax2.text(i, max(p, d) + 2, f"{rate:.0f}%", ha="center", fontsize=10,
             color="#C62828", fontweight="bold")

# ── 5c. Burndown Chart ────────────────────────────────────────────
ax3 = axes[2]

# Sprint 1 Burndown
sprint_start = SPRINT1_START
sprint_end   = SPRINT1_END
total_pts    = s1_planned_pts
sprint_days  = (sprint_end - sprint_start).days

# 이상적 번다운 (직선)
ideal_dates = [sprint_start + timedelta(days=d) for d in range(sprint_days + 1)]
ideal_remaining = [total_pts * (1 - d / sprint_days) for d in range(sprint_days + 1)]

# 실제 번다운: 완료된 이슈 기준 (현재는 close 없으므로 TODAY까지 0 완료)
actual_dates = [sprint_start, TODAY]
actual_remaining = [float(total_pts), float(total_pts - s1_done_pts)]

ax3.plot(ideal_dates, ideal_remaining, "b--", linewidth=1.5, label="이상적 번다운", alpha=0.7)
ax3.plot(actual_dates, actual_remaining, "r-o", linewidth=2, markersize=6, label="실제 번다운")

# 현재 날짜 마크
ax3.axvline(x=TODAY, color="green", linestyle=":", linewidth=1.5, label=f"오늘 ({TODAY.strftime('%m/%d')})")
ax3.fill_between(ideal_dates, ideal_remaining, alpha=0.05, color="blue")

ax3.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax3.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=30, ha="right")

ax3.set_ylabel("잔여 Story Points")
ax3.set_title("Sprint 1 Burndown Chart")
ax3.set_ylim(bottom=0)
ax3.legend(fontsize=9)
ax3.grid(alpha=0.3)

plt.tight_layout()
chart_path = f"{OUTPUT_DIR}/sprint_analytics.png"
plt.savefig(chart_path, bbox_inches="tight")
plt.close()
print(f"\n차트 저장: {chart_path}")

# ── 6. 텍스트 리포트 ──────────────────────────────────────────────
report_path = f"{OUTPUT_DIR}/sprint_analytics_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# SentiVision Sprint Analytics Report\n\n")
    f.write(f"**분석 일자:** {TODAY.strftime('%Y-%m-%d')}  \n")
    f.write(f"**Repository:** {OWNER}/{REPO}  \n\n")

    f.write("## 1. Cycle Time\n\n")
    f.write("| 이슈 | 제목 | 스프린트 | 상태 | Cycle Time(일) |\n")
    f.write("|------|------|----------|------|---------------|\n")
    for _, row in df.iterrows():
        status = "완료" if row["is_closed"] else "진행중"
        ct_label = f"{row['cycle_time_days']:.1f}" if row["is_closed"] else f"{row['cycle_time_days']:.1f} (WIP)"
        sprint_label = f"Sprint {row['sprint']}" if row["sprint"] > 0 else "Backlog"
        f.write(f"| #{row['number']} | {row['title']} | {sprint_label} | {status} | {ct_label} |\n")

    if len(closed_df) > 0:
        f.write(f"\n**평균 Cycle Time:** {closed_df['cycle_time_days'].mean():.1f}일  \n")
        f.write(f"**중앙값:** {closed_df['cycle_time_days'].median():.1f}일  \n")
    else:
        f.write(f"\n> 완료된 이슈 없음 — 현재 WIP Age 평균: {df['cycle_time_days'].mean():.1f}일\n")

    f.write("\n## 2. Velocity\n\n")
    f.write("| 스프린트 | 계획 (pts) | 완료 (pts) | 완료율 | 계획 이슈 수 | 완료 이슈 수 |\n")
    f.write("|----------|-----------|-----------|--------|-------------|-------------|\n")
    for sname, p_pts, d_pts, p_cnt, d_cnt in [
        ("Sprint 1", s1_planned_pts, s1_done_pts, s1_planned_cnt, s1_done_cnt),
        ("Sprint 2", s2_planned_pts, s2_done_pts, s2_planned_cnt, s2_done_cnt),
    ]:
        rate = f"{d_pts/p_pts*100:.0f}%" if p_pts > 0 else "N/A"
        f.write(f"| {sname} | {p_pts} | {d_pts} | {rate} | {p_cnt} | {d_cnt} |\n")

    f.write("\n## 3. Sprint 1 Burndown\n\n")
    f.write(f"- **시작일:** {SPRINT1_START.strftime('%Y-%m-%d')}  \n")
    f.write(f"- **종료일:** {SPRINT1_END.strftime('%Y-%m-%d')}  \n")
    f.write(f"- **총 Story Points:** {total_pts}pts  \n")
    f.write(f"- **완료 Points:** {s1_done_pts}pts  \n")
    f.write(f"- **잔여 Points:** {total_pts - s1_done_pts}pts  \n\n")

    progress_days = (TODAY - SPRINT1_START).days
    elapsed_pct = progress_days / sprint_days * 100
    done_pct = (s1_done_pts / total_pts * 100) if total_pts > 0 else 0
    f.write(f"| 항목 | 값 |\n|------|---|\n")
    f.write(f"| 경과 기간 | {progress_days}/{sprint_days}일 ({elapsed_pct:.0f}%) |\n")
    f.write(f"| 완료율 | {done_pct:.0f}% |\n")
    if elapsed_pct > done_pct:
        f.write(f"| 상태 | ⚠️ 번다운 지연 ({elapsed_pct-done_pct:.0f}%p 뒤처짐) |\n")
    else:
        f.write(f"| 상태 | ✅ 순조로운 진행 |\n")

    f.write("\n## 4. 차트\n\n")
    f.write("![Sprint Analytics](sprint_analytics.png)\n")

print(f"리포트 저장: {report_path}")
print("\n✅ 분석 완료!")
print(f"   차트:   {chart_path}")
print(f"   리포트: {report_path}")
