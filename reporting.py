"""Part 2b - Building the reports."""

import pandas as pd

TOP_5_COLUMNS = [
    "loan_id",
    "customer_name",
    "branch_code",
    "loan_type",
    "status",
    "principal_amount",
    "outstanding",
    "overdue_days",
    "overdue_exposure",
]


def build_branch_report(df):
    """One row per branch, with totals and overdue percentages.

    groupby splits the loans into one pile per branch, works out these
    numbers for each pile, and puts the answers back together.
    """
    out = df.groupby("branch_code").agg(
        total_loans=("loan_id", "count"),
        total_principal=("principal_amount", "sum"),
        total_outstanding=("outstanding", "sum"),
        overdue_exposure=("overdue_exposure", "sum"),
        pct_overdue_30plus=("overdue_30plus", "mean"),
        pct_overdue_60plus=("overdue_60plus", "mean"),
        pct_overdue_90plus=("overdue_90plus", "mean"),
    )

    # The mean of a True/False column is the share that are True,
    # so multiplying by 100 turns it into a percentage.
    out["pct_overdue_30plus"] = out["pct_overdue_30plus"] * 100
    out["pct_overdue_60plus"] = out["pct_overdue_60plus"] * 100
    out["pct_overdue_90plus"] = out["pct_overdue_90plus"] * 100

    out = out.round(2)
    out = out.reset_index()          # turn branch_code back into a normal column
    return out.sort_values("total_outstanding", ascending=False).reset_index(drop=True)


def build_top_5_overdue(df):
    """The five single largest overdue exposures in the whole book."""
    overdue_loans = df[df["overdue_days"] > 0]

    out = overdue_loans.nlargest(5, "overdue_exposure")
    out = out[TOP_5_COLUMNS].round(2)
    return out.reset_index(drop=True)


def build_portfolio_summary(df):
    """Whole-book totals, useful as a check on the branch report."""
    summary = {
        "total_loans": len(df),
        "total_principal": round(df["principal_amount"].sum(), 2),
        "total_outstanding": round(df["outstanding"].sum(), 2),
        "total_overdue_exposure": round(df["overdue_exposure"].sum(), 2),
        "pct_overdue_30plus": round(df["overdue_30plus"].mean() * 100, 2),
        "pct_overdue_60plus": round(df["overdue_60plus"].mean() * 100, 2),
        "pct_overdue_90plus": round(df["overdue_90plus"].mean() * 100, 2),
    }
    return pd.DataFrame([summary])
