import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const reviewDirectory = process.argv.slice(3).find(arg => !arg.startsWith('--'));
const output = reviewDirectory ? resolve(reviewDirectory) : fileURLToPath(new URL('.', import.meta.url));
const bundle = process.argv[2];
const { Workbook, SpreadsheetFile } = await import(pathToFileURL(
  resolve(bundle, '@oai/artifact-tool/dist/artifact_tool.mjs')
).href);
const data = JSON.parse(await readFile(resolve(output, 'Period_Selection_V10_10.json'), 'utf8'));
const native = JSON.parse(await readFile(resolve(output, 'Empirical_PDelta_Readback.json'), 'utf8'));
const book = Workbook.create();
const summary = book.worksheets.add('Reconciliation');
const wall = book.worksheets.add('Wall groups');
const floor = book.worksheets.add('Native floors');

const ink = '#183248';
const teal = '#126762';
const muted = '#EAF4F3';
const source = '#20558C';

function base(sheet, widths, lastRow) {
  sheet.showGridLines = false;
  const last = String.fromCharCode(64 + widths.length);
  const body = sheet.getRange(`A1:${last}${lastRow}`);
  body.format.font = { name: 'Aptos', size: 11, color: ink };
  body.format.rowHeight = 20;
  for (const [index, width] of widths.entries()) {
    const col = String.fromCharCode(65 + index);
    sheet.getRange(`${col}:${col}`).format.columnWidthPx = width;
  }
}

function band(sheet, address, title, fill, size=11) {
  const range = sheet.getRange(address);
  range.merge();
  range.values = [[title]];
  range.format.fill = fill;
  range.format.font = { name: 'Aptos', size, bold: true, color: '#FFFFFF' };
  range.format.rowHeight = size + 16;
}

function header(sheet, address, labels) {
  const range = sheet.getRange(address);
  range.values = [labels];
  range.format.fill = teal;
  range.format.font = { name: 'Aptos', size: 10, bold: true, color: '#FFFFFF' };
  range.format.rowHeight = 26;
}

base(summary, [295, 126, 126, 495], 37);
band(summary, 'A1:D1', 'NBC 105:2025  |  ETABS period and spectrum reconciliation', ink, 16);
band(summary, 'A2:D2', '25 storeys  •  95 m  •  ULS  •  Automatic T1 requires an empirical-period P-Delta run', teal);
header(summary, 'A4:D4', ['Metric', 'X', 'Y', 'Basis']);
const notes = [
  ['Weighted wall area Aw (m²)', 'Grouped X lines, gross length and net area'],
  ['Empirical period (s)', 'NBC §5.1.2'],
  ['1.25 × empirical (s)', 'NBC §5.1.3'],
  ['Automatic P-Delta Rayleigh (s)', 'Centered P-Delta result on verified empirical-period loading'],
  ['Manual analytical period (s)', 'Optional. Replaces automatic Rayleigh and uses the cap.'],
  ['Direct T1 override (s)', 'Optional. Uses your exact value and skips the cap.'],
  ['NBC minimum (s)', 'Lesser of the analytical period and amplified empirical'],
  ['Active T1 (s)', 'Used for Ch, Cd, exponent k and static shear'],
  ['Period selection', 'Enter at most one manual value per direction'],
  ['Directional Ritz period (s)', 'Native modal period, rounded export'],
  ['Tn at 90% mass (s)', 'Native Ritz modes 6 X and 8 Y'],
  ['Static Ch(T1)', 'NBC Soil C equivalent-static spectrum, 0 to 6 s'],
  ['ULS Cd', 'Z = 0.35, I = 1, Rμ = 3.5, Ωu = 1.4'],
  ['SLS Cd', 'Same T1 sensitivity, Ωs = 1.2'],
  ['Height exponent k', 'NBC ESM force distribution'],
  ['Native seismic weight (kN)', 'ETABS auto-seismic assignment, base excluded'],
  ['Corrected static reference (kN)', 'ULS Cd × W'],
  ['Saved V10.7 ESM and RS (kN)', 'Archived exact-normalized results'],
  ['Change from saved static (%)', 'Corrected reference / saved ESM − 1'],
  ['Prior RS before V10.7 normalization (kN)', 'Historical excitation from the scaling workbook'],
  ['Saved RS input scale (m/s²)', 'Axis-specific scale stored in the native model'],
  ['NBC MRSM input scale (m/s²)', 'g × Z × I / (Rμ × Ωu), both axes'],
  ['Projected code-basis RS shear (kN)', 'Linear rescale of saved result, pending native run'],
  ['Projected RS force multiplier', 'Recalculate from new native shear after rerun'],
  ['§7.5 displacement multiplier', 'Apply to baseline drift/displacement, see §5.5'],
];
summary.getRange('A5:D29').values = notes.map(([label,note]) => [label, null, null, note]);
band(summary, 'A31:D31', 'Preliminary ETABS run  |  Apply the unamplified empirical period', ink);
summary.getRange('A32:D35').values = [
  ['Empirical reference coefficient Cd', null, null, 'Apply to the EQX / EQY load patterns'],
  ['Empirical reference exponent k', null, null, 'Use for the preliminary floor-force distribution'],
  ['Empirical reference base shear (kN)', null, null, 'Check against the new native export'],
  ['Empirical P-Delta readback', null, null, 'Verified after the case, loads and export match'],
];
for (const [i, axis] of ['X','Y'].entries()) {
  const col = i === 0 ? 'B' : 'C';
  const d = data.directions[axis];
  const start = i === 0 ? 4 : 29;
  const end = start + 24;
  const wallRows = i === 0 ? 'G4:G5' : 'G6:G8';
  const f = {
    5: `=SUM('Wall groups'!${wallRows})`,
    6: `=0.075/SQRT(${col}5)*'Wall groups'!I4^0.75`, 7: `=1.25*${col}6`,
    8: `=IF(${col}35="Verified",2*PI()*SQRT(SUM('Native floors'!J${start}:J${end})/SUM('Native floors'!I${start}:I${end})),"")`,
    11: `=IF(${col}9="",IF(${col}8="","",MIN(${col}7,${col}8)),IF(AND(ISNUMBER(${col}9),${col}9>0),MIN(${col}7,${col}9),""))`,
    12: `=IF(${col}10="",${col}11,IF(AND(${col}9="",ISNUMBER(${col}10),${col}10>0,${col}10<=6),${col}10,""))`,
    13: `=IF(${col}12="",IF(AND(${col}9="",${col}10="",${col}8=""),"Awaiting ETABS","Check inputs"),IF(${col}10<>"","Direct override",IF(${col}9<>"","Manual + cap","P-Delta + cap")))`,
    16: `=IF(${col}12="","",IF(${col}12<=1,2.5,IF(${col}12<=4,2.5/${col}12,10/${col}12^2)))`,
    17: `=IF(${col}16="","",${col}16*0.35/(3.5*1.4))`,
    18: `=IF(${col}16="","",0.2*${col}16*0.35/1.2)`,
    19: `=IF(${col}12="","",MIN(2,MAX(1,1+(${col}12-0.5)/2)))`,
    21: `=IF(${col}17="","",${col}17*${col}20)`,
    23: `=IF(${col}21="","",${col}21/${col}22-1)`,
    26: "='Native floors'!L4*0.35/(3.5*1.4)",
    27: `=${col}22*${col}26/${col}25`,
    28: `=IF(${col}21="","",MAX(1,${col}21/${col}27))`,
  };
  for (const [row, formula] of Object.entries(f)) summary.getRange(`${col}${row}`).formulas = [[formula]];
  const raw = {14:d.ritz_s, 15:d.tn90_s, 20:d.native_weight_kN, 22:d.saved_esm_and_rs_kN,
               24:d.archived_pre_normalization_rs_kN, 25:d.saved_normalized_sf_m_per_s2, 29:1,
               32:d.empirical_reference.cd_uls, 33:d.empirical_reference.k,
               34:d.empirical_reference.updated_esm_minimum_kN,
               35:native.directions[axis].empirical_reference_verified ? 'Verified' : 'Pending'};
  for (const [row, value] of Object.entries(raw)) {
    const cell = summary.getRange(`${col}${row}`);
    cell.values = [[value]];
    cell.format.font.color = source;
  }
}
summary.getRange('B5:C29').setNumberFormat('0.000000');
summary.getRange('B9:C10').format.fill = '#FFF0BE';
for (const row of [20,21,22,24,27]) summary.getRange(`B${row}:C${row}`).setNumberFormat('#,##0.000');
summary.getRange('B32:C33').setNumberFormat('0.000000');
summary.getRange('B34:C34').setNumberFormat('#,##0.000');
summary.getRange('B23:C23').setNumberFormat('0.00%');
for (const row of [12,21,28]) {
  summary.getRange(`A${row}:D${row}`).format.fill = muted;
  summary.getRange(`A${row}:C${row}`).format.font.bold = true;
}
band(summary, 'A37:D37', 'Workflow and P-Delta provenance  |  ETABS period review README', ink);

base(wall, [76,110,110,132,132,119,120,45,118], 10);
band(wall, 'A1:I1', 'Reviewed shear-wall groups', ink, 16);
header(wall, 'A3:G3', ['Axis / line','Full L (m)','t (m)','Opening count','Clear width (m)','Net area (m²)','Aw (m²)']);
wall.getRange('I3').values = [['Height H (m)']];
wall.getRange('I4').values = [[data.height_m]];
wall.getRange('A4:E8').values = ['X','Y'].flatMap(axis => data.directions[axis].walls.map(
  (w,i) => [axis === 'X' ? ['X / B','X / D'][i] : `Y / ${i+1}`, w.length_m, w.thickness_m, w.opening_count, w.opening_width_m]
));
for (let row=4;row<=8;row++) {
  wall.getRange(`F${row}:G${row}`).formulas = [[
    `=C${row}*(B${row}-D${row}*E${row})`,
    `=F${row}*(0.2+MIN(B${row}/$I$4,0.9)^2)`,
  ]];
}
wall.getRange('F4:G8').setNumberFormat('0.000000');
wall.getRange('B4:E8').format.font.color = source;

base(floor, [65,135,80,85,100,100,105,104,112,122,40,115], 53);
band(floor,'A1:L1','ETABS import evidence  |  Centered P-Delta, step 1, diaphragm D1',ink,16);
header(floor,'A3:J3',['Axis','Case','Storey','Elev. (m)','Wi (kN)','Fi (kN)','CM δ (m)','CM T (kN·m)','Fi × δ (kN·m)','Wi × δ² / g']);
floor.getRange('L3').values = [['g (m/s²)']];
floor.getRange('L4').values = [[data.gravity_m_per_s2]];
floor.getRange('A4:H53').values = ['X','Y'].flatMap(axis => native.directions[axis].rows.map(row => [
  axis, native.directions[axis].case, row.story, row.level_m, row.weight_kN, row.force_kN, row.displacement_m, row.torsion_kNm,
]));
for (let row=4;row<=53;row++) {
  floor.getRange(`I${row}:J${row}`).formulas = [[`=F${row}*G${row}`, `=E${row}*G${row}^2/$L$4`]];
}
floor.getRange('A4:H53').format.font.color = source;
floor.getRange('D4:J53').setNumberFormat('0.000000');
floor.freezePanes.freezeRows(3);
if (process.argv.includes('--check-inputs')) {
  const x = name => summary.getRange(name).values[0][0];
  const write = (cell, value) => { summary.getRange(cell).values = [[value]]; };
  const equal = (actual, expected) => {
    if (typeof expected === 'number' ?
        (!Number.isFinite(actual) || Math.abs(actual - expected) > 1e-10) : actual !== expected) {
      throw new Error(`Expected ${expected}, received ${actual}`);
    }
  };
  const eligible = native.directions.X.empirical_reference_verified;
  if (eligible) equal(x('B12'), Math.min(native.directions.X.period_s, data.directions.X.empirical_cap_s));
  else equal(x('B13'), 'Awaiting ETABS');
  write('B9', 2.2);
  equal(x('B12'), data.directions.X.empirical_cap_s);
  equal(x('B13'), 'Manual + cap');
  write('B10', 0.75);
  equal(x('B13'), 'Check inputs');
  write('B9', null);
  equal(x('B12'), 0.75);
  equal(x('B16'), 2.5);
  equal(x('B13'), 'Direct override');
  if (eligible) equal(x('B11'), Math.min(native.directions.X.period_s, data.directions.X.empirical_cap_s));
  else equal(x('B11'), '');
  write('B10', -1);
  equal(x('B13'), 'Check inputs');
  write('B10', null);
  equal(x('B13'), eligible ? 'P-Delta + cap' : 'Awaiting ETABS');
}
const file = await SpreadsheetFile.exportXlsx(book);
await file.save(resolve(output, 'NBC105_2025_95m_12m_Empirical_First_V10_10.xlsx'));
const preview = await book.render({sheetName:summary.name, range:'A1:D37', format:'png'});
await writeFile(resolve(output, 'Workbook_Empirical_First_Preview.png'), new Uint8Array(await preview.arrayBuffer()));
