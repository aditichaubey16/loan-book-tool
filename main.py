"""Loan book cleaning and reporting tool.

Run with:  python main.py
"""

import cleaning
import metrics
import reporting

INPUT_FILE = "loan_book_sample.csv"
OUTPUT_FOLDER = "output"


def main():
    raw = cleaning.load_data(INPUT_FILE)
    print("Loaded", len(raw), "rows from", INPUT_FILE)

    good, quarantined = cleaning.clean_loan_book(raw)
    print("  ", len(good), "clean rows")
    print("  ", len(quarantined), "rows set aside")

    report_data = metrics.add_all_metrics(good)

    branch_report = reporting.build_branch_report(report_data)
    top_5_overdue = reporting.build_top_5_overdue(report_data)
    summary = reporting.build_portfolio_summary(report_data)

    branch_report.to_csv(OUTPUT_FOLDER + "/branch_report.csv", index=False)
    top_5_overdue.to_csv(OUTPUT_FOLDER + "/top_5_overdue.csv", index=False)
    summary.to_csv(OUTPUT_FOLDER + "/portfolio_summary.csv", index=False)
    quarantined.to_csv(OUTPUT_FOLDER + "/quarantined_rows.csv", index=False)

    print("\nReports saved in the", OUTPUT_FOLDER, "folder")
    print("\nBranch report:")
    print(branch_report.to_string(index=False))
    print("\nTop 5 overdue exposures:")
    print(top_5_overdue.to_string(index=False))


if __name__ == "__main__":
    main()
