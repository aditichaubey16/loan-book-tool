"""Part 1 - Data cleaning.

Each function takes a table in and gives a new table back, so they can be
run one after another as a pipeline. No function changes the table it is given.
"""

import pandas as pd


def load_data(csv_path):
    """Read the CSV file into a table."""
    return pd.read_csv(csv_path)


def remove_duplicates(df):
    """Delete rows that are identical in every column."""
    out = df.copy()                       # work on a copy, leave the original alone
    out = out.drop_duplicates()           # keeps the first of each repeated row
    return out.reset_index(drop=True)     # renumber the rows 0, 1, 2, ...


def add_problem_column(df):
    """Add an empty 'problem' column. Bad rows get a reason written here later."""
    out = df.copy()
    out["problem"] = ""
    return out


def fix_text_columns(df):
    """Remove stray spaces and make text uppercase, so 'mum01' becomes 'MUM01'.

    branch_code is what the brief asks for. loan_type and status get the same
    treatment because status is used later to decide which loans are settled.
    """
    out = df.copy()
    out["branch_code"] = out["branch_code"].str.strip().str.upper()
    out["loan_type"] = out["loan_type"].str.strip().str.upper()
    out["status"] = out["status"].str.strip().str.upper()
    return out


def fix_dates(df):
    """Turn the date text into real dates.

    The file uses two formats, so we try both. errors="coerce" means a value
    that cannot be read becomes blank instead of crashing the program.
    Dates that fail both attempts (like 31-02-2023, which does not exist)
    are marked as a problem.
    """
    out = df.copy()
    date_text = out["disbursement_date"]

    # Keep the original text so the quarantine file shows what was wrong.
    out["disbursement_date_raw"] = date_text

    try_year_first = pd.to_datetime(date_text, format="%Y-%m-%d", errors="coerce")
    try_day_first = pd.to_datetime(date_text, format="%d-%m-%Y", errors="coerce")

    # Use the year-first result; where that is blank, fall back to day-first.
    out["disbursement_date"] = try_year_first.fillna(try_day_first)

    bad_dates = out["disbursement_date"].isna()
    out.loc[bad_dates, "problem"] = "invalid_disbursement_date"
    return out


def flag_missing_principal(df):
    """Mark rows that have no principal amount. They cannot be valued."""
    out = df.copy()
    missing = out["principal_amount"].isna()

    out["is_missing_principal"] = missing                      # the flag the brief asks for
    out.loc[missing, "problem"] = "missing_principal_amount"    # and set aside from the report
    return out


def split_good_and_quarantined(df):
    """Separate rows with no problem from rows that have one."""
    out = df.copy()

    good = out[out["problem"] == ""]           # blank problem = usable row
    quarantined = out[out["problem"] != ""]    # anything written = set aside

    # The clean table does not need the empty problem column.
    good = good.drop(columns=["problem"])

    return good.reset_index(drop=True), quarantined.reset_index(drop=True)


def clean_loan_book(raw):
    """Run every cleaning step in order.

    Order matters: duplicates are removed first, so a problem row is not
    counted twice. Returns (clean rows, quarantined rows).
    """
    step1 = remove_duplicates(raw)
    step2 = add_problem_column(step1)
    step3 = fix_text_columns(step2)
    step4 = fix_dates(step3)
    step5 = flag_missing_principal(step4)
    return split_good_and_quarantined(step5)
