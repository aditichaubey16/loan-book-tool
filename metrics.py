"""Part 2a - Numbers we work out ourselves.

The file does not say how much money is still owed on each loan, so we
calculate it from the EMI, the interest rate and the number of EMIs left.
"""

import pandas as pd

# A loan in one of these states has nothing left to repay.
SETTLED_STATUSES = ["CLOSED", "WRITTEN_OFF"]


def add_remaining_months(df):
    """How many EMIs are still to be paid."""
    out = df.copy()
    out["remaining_months"] = out["tenure_months"] - out["emi_paid_count"]

    # A borrower who paid extra would give a negative answer, so stop at zero.
    out["remaining_months"] = out["remaining_months"].clip(lower=0)
    return out


def add_outstanding(df):
    """How much is still owed today.

    This is the value today of all the EMIs still to be paid:

        outstanding = EMI * (1 - (1 + r) ** -n) / r

    where r is the monthly interest rate and n is the number of EMIs left.

    We do not use "principal x share of EMIs unpaid", because an EMI is
    mostly interest at the start of a loan and mostly repayment at the end.
    Counting payments made would understate what is still owed.
    """
    out = df.copy()

    monthly_rate = out["interest_rate"] / 12 / 100
    n = out["remaining_months"]

    out["outstanding"] = out["emi_amount"] * (1 - (1 + monthly_rate) ** -n) / monthly_rate

    # Loans that are finished or written off have nothing left to repay.
    settled = out["status"].isin(SETTLED_STATUSES)
    out.loc[settled, "outstanding"] = 0.0

    out["outstanding"] = out["outstanding"].round(2)
    return out


def add_overdue_buckets(df):
    """True/False columns for the 30+, 60+ and 90+ day buckets.

    The buckets overlap on purpose: a loan 95 days late is in all three,
    because "30+" means at least 30 days. 90+ is the regulatory NPA line.
    """
    out = df.copy()
    out["overdue_30plus"] = out["overdue_days"] >= 30
    out["overdue_60plus"] = out["overdue_days"] >= 60
    out["overdue_90plus"] = out["overdue_days"] >= 90
    return out


def add_overdue_exposure(df):
    """How much money is at risk, not just how many loans are late.

    A loan paying on time risks nothing. A late loan risks its whole
    remaining balance.
    """
    out = df.copy()
    out["overdue_exposure"] = 0.0

    is_overdue = out["overdue_days"] > 0
    out.loc[is_overdue, "overdue_exposure"] = out.loc[is_overdue, "outstanding"]
    return out


def add_all_metrics(df):
    """Add every calculated column, in order."""
    step1 = add_remaining_months(df)
    step2 = add_outstanding(step1)
    step3 = add_overdue_buckets(step2)
    step4 = add_overdue_exposure(step3)
    return step4
