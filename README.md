# Proxy replication: Fare Game

This repository is a small, transparent proxy replication inspired by Burak Aydin, Emre Parmaksiz, and Ronnie Sircar, "Fare Game: A Mean Field Model of Stochastic Intensity Control in Dynamic Ticket Pricing" (arXiv:2506.13088).

## Scope

The paper develops a finite-horizon mean-field game for sellers of perishable inventory. The original work is primarily structural and numerical; it explicitly presents the airfare comparison as qualitative rather than a full calibration. This project therefore reproduces the qualitative experiment: compare a non-competitive seller with a competition-aware seller using route-level airfare summaries.

## Data

`data/route_summary.csv` is a derived summary from the public Kaggle Flight Prices dataset. It contains route, observed-day count, mean fare, standard deviation, and maximum fare.

Source: https://www.kaggle.com/datasets/danieldeng054/flightprices-preprocessed-v1

## Run

```text
python replicate.py
```

The script writes `results.csv` with route-level mean prices, expected sales, and revenue under the two competition settings.

## Limitations

This is not a claim that the paper's coupled HJB-Kolmogorov solver has been reproduced exactly. It is a student-built, finite-horizon best-response proxy using publicly available route summaries.

