# Dictionaries

The `dictionary/` folder contains JSON files that drive the app's behavior:

| File | Purpose |
| --- | --- |
| `categories-dictionary.json` | Maps notes/keywords to transaction categories. |
| `labels-dictionary.json` | Maps notes/keywords to labels. |
| `import-dictionary.json` | Column mappings used when importing external CSVs. |
| `ignore-dictionary.json` | Rules for skipping rows during import. |

## Ignoring rows on import

`ignore-dictionary.json` defines rules that prevent matching rows from being copied into `allTransactions.csv`.

Each rule contains a list of `conditions`. A row is ignored when **all conditions inside a rule** match (logical AND). Multiple rules are combined with logical OR.

```json
{
  "ignore_rules": [
    {
      "conditions": [
        { "column": "Amount",   "value": "100" },
        { "column": "Name",     "value": "VAT" },
        { "column": "Currency", "value": "PLN" }
      ]
    },
    {
      "conditions": [
        { "column": "Category", "value": "Food" }
      ]
    }
  ]
}
```

In the example above, a row is ignored when:

- `Amount = 100` **AND** `Name = VAT` **AND** `Currency = PLN`
- **OR** `Category = Food`

## Column mapping aliases

Each entry in `import-dictionary.json`'s `column_mapping` maps a canonical column name (`Date`, `Amount`, `Note`, etc.) to a list of aliases the importer will recognize from your bank's CSV header. **You do NOT need to repeat the canonical name in its own alias list** — date and amount normalization apply based on the canonical name itself, not on alias-list membership.

For example, both of these are equivalent:

```json
"Date": ["Date", "#Data operacji", "Data transakcji"]
"Date": ["#Data operacji", "Data transakcji"]
```

## Force-update behavior

When you check **"Force categories update"** before clicking **Run Processing**, every row in the selected range is re-evaluated against the dictionary. Manually-set categories are preserved when no dictionary rule matches — only empty cells become `Other`. If a dictionary rule DOES match, force-update overwrites the existing category with the matched one. See [ADR-0005](architecture/decisions/adr-0005-force-update-other.md) for the full truth table.
