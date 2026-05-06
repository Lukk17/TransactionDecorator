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

## Force-update behavior

When you check **"Force categories update"** before clicking **Run Processing**, every row in the selected range is re-categorized from the dictionary. Rows whose `Note` matches no keyword are reset to `Other` — even if they previously had a manually-set category. See [ADR-0005](architecture/decisions/adr-0005-force-update-other.md) for the rationale and how to scope a force-update to specific rows.
