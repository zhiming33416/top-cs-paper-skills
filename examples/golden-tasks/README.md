# Golden Task Board

These seven cases are synthetic demonstrations of workflow contracts, not examples of accepted papers or model-quality rankings. The inputs never contain real manuscripts, reviews, experiment data, or source full text.

| Task | Input | Required artifact | Boundary |
| --- | --- | --- | --- |
| evidence | claims, BibTeX metadata, optional note path | citation ledger and claim map | identity does not prove support |
| writing | result notes and contribution | claim–evidence outline | no invented result or citation |
| polishing | supplied prose/LaTeX | revision ledger | preserve facts and syntax |
| figure | synthetic CSV and figure brief | render spec and export bundle | data/spec/provenance QA |
| reviewer | synthetic manuscript summary | issue board | calibrated author-side risk |
| response | synthetic reviewer concern | response and revision ledger | no invented promise or change |
| workflow | metadata-only project state | advisory/strict status report | no copied private material |

The machine-readable board is [board.yaml](board.yaml). Every case names the public test modules that verify its assertion in the `verified_by` field; CI checks both the board structure and that every referenced test module exists. The board is summarized on the repository homepage.
