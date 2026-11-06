def solve(x):
    eligible = sorted(
        [r for r in x["feedback"] if r["resolved_at"] <= x["cutoff"] and r["split"] == "calibration"],
        key=lambda r: r["id"],
    )
    losses = []
    for threshold in sorted(x["candidates"]):
        loss = 0
        for r in eligible:
            if r["strength"] < threshold:
                loss += 1
            elif not r["correct"]:
                loss += 3
        losses.append({"threshold": threshold, "cost": loss})
    best = min(losses, key=lambda r: (r["cost"], abs(r["threshold"] - x["current_threshold"]), r["threshold"]))
    return {"chosen_threshold": best["threshold"], "losses": losses, "evidence_ids": [r["id"] for r in eligible]}
