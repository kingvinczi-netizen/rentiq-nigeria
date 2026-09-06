# RentIQ Nigeria

Annual residential rent estimates for Lagos, from listing data and published
electricity-supply bands. Live at https://rentiq.streamlit.app

MSc Data Science project, Pan-Atlantic University. Victory Chisom Ezeala.

## Model

Stacked ensemble of XGBoost, LightGBM and CatBoost, tuned with Optuna and combined
by a Ridge meta-learner. Target is log annual rent. 10,999 listings collected in
May 2026 from NigeriaPropertyCentre, PropertyPro and PrivateProperty across 120
Lagos areas.

| Metric | Value |
|---|---|
| Test R2 | 0.869 |
| Naive neighbourhood-median baseline | 0.711 |
| Linear regression, same features | 0.831 |
| MAPE | 64.2% |
| 10-fold CV | 0.882, sd 0.009 |
| Prediction interval coverage | 79.5% against an 80% target |

Accuracy varies a lot by segment: about 29% MAPE in GRA, which supplies most
queries, and considerably worse in the Island, Outskirt and Suburb tiers. Island
error is driven by unlisted attributes (floor area, finishing grade, waterfront
position); Outskirt and Suburb by having roughly fifty test rows each.

## Two things worth knowing

**Location aggregates and leakage.** `neighbourhood_median_rent`, `area_median_rent`
and `tier_median_rent` are derived from the target. When scoring the model they are
computed from training rows only and rebuilt inside every cross-validation fold,
otherwise held-out rows are graded against a median their own rent helped form. With
2,351 distinct neighbourhood labels across 10,999 listings the median neighbourhood
holds one listing, so a whole-dataset median reproduces that row's own rent about a
quarter of the time. The shipped model fits on all rows, which is correct at
inference because there is no held-out set, but the reported metrics above come from
the training-only run.

**Prediction intervals, not confidence intervals.** The P10 to P90 range describes
uncertainty about one property, not about a population average. Plain quantile
regression covered only 64.2% against an 80% target, so the interval is conformalised:
widened by `conformal_q` log units from `artifacts/model_card.json`, which restores
79.5%. Coverage holds on average rather than uniformly, and is weakest in the Suburb
tier at 55.1%.

Prices are asking prices from listing sites, not transacted rents. Lagos rents are
negotiated, so treat the P10 bound as the more realistic anchor.

## Coverage

41 areas are served directly, each backed by at least 5 listings and carrying its
`listing_count`; the app flags any area with fewer than 30. A further 124 aliases map
estate- and street-level names onto a parent area, for 165 searchable locations.

Three candidate areas were left out because their scrape buckets are not clean: the
listings returned under those area names span three or more location tiers and rents
across more than a tenfold range, so an area median computed from them describes no
real market. Six areas already in the lookup have the same problem to varying degrees
and are unchanged here, since altering what the tool already serves is a separate
decision. `iyana-ipaja` is the clearest case: 110 listings spanning all seven tiers
with a median of N5.25m, against a local market that runs roughly N1m to N3.5m. Aliases
added automatically use a multiplier of 1.0: with only a handful of listings behind them
a derived premium or discount would be noise, so they simply return the parent area's
estimate. The hand-curated multipliers already in the file are unchanged.

## Layout

```
app.py                        Streamlit application
artifacts/stacked_ensemble.pkl  xgb + lgb + cat + Ridge meta-learner
artifacts/lgb_p10.pkl           P10 quantile model
artifacts/lgb_p90.pkl           P90 quantile model
artifacts/model_card.json       metrics and the conformal adjustment
artifacts/area_lookup.csv       41 areas with pre-computed location features
artifacts/area_aliases.csv      124 aliases, extending coverage to 165 locations
data/rentiq_master.csv          the cleaned dataset
```

Seeded with 42 throughout: the split, the Optuna samplers, every fold and every model.
