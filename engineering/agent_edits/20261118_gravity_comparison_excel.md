# Gravity support comparison workbook export

Editor OpenAI Codex desktop. Exact model build unknown. Base `815068872288af3327b2f49dd7bb27efa83fee40`, branch `fix/gravity-comparison-excel`.

The existing comparison exporter and workbook publisher own the fix. The evidence status sheet converts list values to comma-separated text while JSON keeps its arrays. The workbook publisher supplies atomic replacement. Changes affect the exporter, its source guide and its regression test.

The regression reproduced the Excel list error before the fix. After the fix, 24 focused checks passed. A separate export using the three registered native results produced an XLSX with the five expected sheets and 97 comparison rows. This edit has no effect on ETABS or OpenSees calculations or engineering acceptance.
