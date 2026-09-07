[README.md](https://github.com/user-attachments/files/31923814/README.md)
# Loan Book Cleaning and Reporting Tool

This tool takes a raw loan book file from a housing finance company, cleans up
the messy data, works out how much money is still owed, and produces a report
for each branch.

## How to run it

You need Python 3 and pandas.

```
pip install pandas
```

Keep all the files in one folder and run:

```
python main.py
```

That does everything: cleaning, calculations, and saving the reports.

## Files

| File | What it does |
|---|---|
| `cleaning.py` | Part 1 - cleans the raw data |
| `metrics.py` | Works out the outstanding amount and the overdue buckets |
| `reporting.py` | Part 2 - builds the branch report and the top 5 list |
| `main.py` | Runs everything and saves the output files |

I wrote each step as its own small function. Every function takes a table in
and gives a new table back, and none of them changes the table it was given.
This way the steps can be run one after another, and I can check the result
after any step.

## Output files

All output goes into the `output` folder.

| File | What is in it |
|---|---|
| `branch_report.csv` | One row per branch, with totals and overdue percentages |
| `top_5_overdue.csv` | The 5 biggest overdue loans in the whole book |
| `portfolio_summary.csv` | Totals for the whole book, as a check |
| `quarantined_rows.csv` | The rows I set aside, with the reason for each |

# Part 1 - Cleaning

| Function | What it does |
|---|---|
| `load_data` | Reads the CSV file |
| `remove_duplicates` | Deletes rows that are the same in every column |
| `add_problem_column` | Adds an empty column to record any problems |
| `fix_text_columns` | Removes extra spaces and makes text uppercase |
| `fix_dates` | Changes the date text into real dates |
| `flag_missing_principal` | Marks rows with no principal amount |
| `split_good_and_quarantined` | Splits the good rows from the bad ones |
| `clean_loan_book` | Runs all the steps in order |

I remove duplicates first. The file has 15 rows with a missing principal
amount, but one of them is a duplicate row, so only 14 are left after that
step. If I flagged them first I would have counted one row twice.

## What I found in the data

```
805  rows in the file
 -5  duplicate rows
----
800
-17  rows set aside
----
783  clean rows
```

The 17 rows I set aside were:

| Problem | Rows |
|---|---|
| No principal amount | 14 |
| Date that does not exist | 3 |

I also found 21 rows where the branch code was in small letters, like `mum01`
instead of `MUM01`. This made 6 branches look like 12 branches. Fixing the
capital letters joins them back together.

# Part 2 - Working out the numbers

## How much is still owed

The file does not have an outstanding amount, so I had to work it out.

The obvious way is to say "94 of 120 EMIs are paid, so 78% is done, so 22% of
the loan is left". **This is wrong.** An EMI is a fixed amount, but what it is
made of changes. At the start most of the EMI is interest and only a little
repays the loan. Near the end it is the other way round. So after 78% of the
payments, much more than 22% of the loan is still owed.

What I did instead is work out what the remaining EMIs are worth today:

```
outstanding = EMI * (1 - (1 + r) ** -n) / r
```

where `r` is the monthly interest rate and `n` is the number of EMIs left.

A small example. If the EMI is 1,000, the rate is 12% a year (so 1% a month),
and 3 EMIs are left:

```
outstanding = 1000 * (1 - 1.01 ** -3) / 0.01 = 2,940.99
```

You will pay 3,000 over the next 3 months, but you only owe 2,940.99 today.
The 59 difference is interest that has not been charged yet.

The difference this makes on the real data is large:

| Method | Total outstanding |
|---|---|
| 94 of 120 EMIs paid, so 22% left | about 74 crore |
| Value of the remaining EMIs | about 89.5 crore |

The simple method comes out about 17% below the correct figure. On one loan
(HFL202400001) it gives 1.78 lakh instead of 2.71 lakh, which is 34% too low.
Loans early in their life are understated the most, because that is when the
gap between payments made and loan repaid is widest.

## Overdue buckets

I made three True/False columns for 30+, 60+ and 90+ days overdue. These
overlap on purpose. A loan 95 days late counts in all three, because "30+"
means at least 30 days.

90+ days is the important one. In India that is the line where a loan becomes
a Non Performing Asset, and the lender has to set money aside against it.

## Overdue exposure

Counting late loans is not enough, because ten small late loans matter less
than one big one. So I also worked out how much money is at risk: a loan
paying on time risks nothing, and a late loan risks its whole remaining
balance. The top 5 report uses this.

# What the report shows

Total outstanding across the book is about 89.5 crore, with about 16 crore of
that on loans that are overdue.

**MUM01 has the weakest book.** Its 60+ and 90+ percentages are exactly the
same, at 12.28%. Every other branch drops between the two, which means some of
their late loans get back on track. At MUM01 not one does. Every loan that
reaches 60 days late goes on to become an NPA. MUM01 also has the highest 90+
rate, nearly 3 times the 4.48% at PUN02.

MUM01 is also the smallest book by outstanding amount, so this is a credit
quality problem, not a size problem.

# My decisions

**I did not fix the bad dates.** All 3 of them say `31-02-2023`. There is no
31st of February, so this date is wrong. It could be a typing mistake for
28-02, or 31-01, or 31-03. I do not know which, so guessing would mean making
up data. I set these rows aside instead so someone can check the original
system.

These 3 rows do have correct principal and EMI values, and the disbursement
date is not used in any of the numbers I report. So another option was to keep
them and only mark the date as bad. I chose to set them aside because the
brief asked for invalid rows to be quarantined.

**I did not fill in the missing principal amounts.** I could work them out
from the EMI, interest rate and tenure. I decided not to, because then the
report would have made up numbers mixed with real ones, and no one reading it
could tell the difference.

**I told pandas the date format instead of letting it guess.** The file has
two date formats. If I let pandas guess, a date like `03-04-2024` could be
read as 3 April or as 4 March, and it might read different rows differently
without giving any error. So I try both formats myself, and anything that
fits neither gets marked as a problem.

**Closed and written off loans are set to zero outstanding.** For a closed
loan this is clearly right. For a written off loan it is a choice: the lender
has removed it from its books, but in practice it often still tries to recover
the money. I took the more conservative view and treated it as zero.

**I also cleaned `loan_type` and `status`.** The brief only asked for
`branch_code`. But I use `status` to decide which loans are settled, and if
one row said `closed` in small letters my check would miss it and the
outstanding figure would be wrong.

**I strip spaces even though there are none.** No branch code in this file has
extra spaces. I still remove them, in case a future file does. The same goes
for the check that stops remaining months going below zero: no borrower in
this file paid early, but the check is there if one does.

# Things I did not do

**One problem is saved per row.** If a row had two problems, the second one
would replace the first. No row in this file has two problems, so my output is
correct, but I would need to change this for a different file.

**Written off loans show 0 days overdue in the source file.** All 39 of them.
This looks wrong, because a written off loan should be very overdue. I left
the data as it is rather than changing it, but it means my overdue percentages
are slightly lower than the real position. This is worth checking with whoever
owns the source system.

**I only checked the four problems in the brief.** A real file might have
other issues, like an interest rate that looks wrong, or more EMIs paid than
the loan tenure. I did not check for those.
