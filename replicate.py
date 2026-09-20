"""Proxy replication of the qualitative Fare Game experiment.

Standard-library only. The paper's full model is a coupled mean-field game;
this script keeps the finite-horizon price/intensity/competition mechanism
visible while using a small route-summary proxy dataset.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "route_summary.csv"
OUT = ROOT / "results.csv"


def load_routes() -> list[dict[str, float | str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        return [
            {
                "route": row["route"],
                "mean": float(row["y_mean"]),
                "std": float(row["y_std"]),
                "max": float(row["y_max"]),
            }
            for row in csv.DictReader(handle)
        ]


def demand_intensity(price: float, reference_price: float, competition: float, scarcity: float) -> float:
    """A decreasing Poisson-style arrival intensity."""
    relative_price = max(0.25, price / reference_price)
    price_sensitivity = math.exp(-1.35 * (relative_price - 1.0))
    competitive_pressure = 1.0 + competition * scarcity
    return max(0.01, 0.32 * price_sensitivity * competitive_pressure)


def solve_route(reference_price: float, fare_std: float, competition: float) -> tuple[float, float, float]:
    horizon = 30
    inventory = max(12.0, 0.20 * reference_price / max(fare_std, 1.0) * 40.0)
    price_grid = [reference_price * (0.65 + 0.05 * i) for i in range(18)]
    policy = [reference_price for _ in range(horizon)]

    for _ in range(60):
        population_price = sum(policy) / horizon
        updated: list[float] = []
        for t in range(horizon):
            remaining = (horizon - t) / horizon
            scarcity = 1.0 + (1.0 - remaining)
            scores = []
            for price in price_grid:
                intensity = demand_intensity(price, population_price, competition, scarcity)
                expected_sales = min(inventory / horizon, intensity * remaining)
                holding_penalty = 0.02 * fare_std * max(0.0, remaining - 0.5)
                scores.append((price - holding_penalty) * expected_sales)
            updated.append(price_grid[max(range(len(scores)), key=scores.__getitem__)])
        policy = [0.75 * old + 0.25 * new for old, new in zip(policy, updated)]

    expected_sales = sum(
        demand_intensity(price, sum(policy) / horizon, competition, 1.0 + t / horizon)
        for t, price in enumerate(policy)
    )
    expected_sales = min(inventory, expected_sales)
    mean_price = sum(policy) / horizon
    expected_revenue = mean_price * expected_sales
    return mean_price, expected_sales, expected_revenue


def main() -> None:
    rows = []
    for route in load_routes()[:20]:
        base = solve_route(route["mean"], route["std"], competition=0.0)
        competitive = solve_route(route["mean"], route["std"], competition=0.35)
        rows.append(
            {
                "route": route["route"],
                "proxy_fare_mean": f"{route['mean']:.4f}",
                "no_competition_mean_price": f"{base[0]:.4f}",
                "no_competition_expected_sales": f"{base[1]:.4f}",
                "no_competition_revenue": f"{base[2]:.4f}",
                "competition_mean_price": f"{competitive[0]:.4f}",
                "competition_expected_sales": f"{competitive[1]:.4f}",
                "competition_revenue": f"{competitive[2]:.4f}",
            }
        )

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.name} for {len(rows)} routes")


if __name__ == "__main__":
    main()

