/**
 * Generic CSV export utility.
 *
 * Usage:
 *   exportToCsv('filename.csv', columns, rows)
 *
 * columns: Array of { label: string, key?: string, transform?: (row) => string, formula?: boolean }
 *   - key: direct property lookup on each row
 *   - transform: custom function for derived values; takes priority over key
 *   - formula: if true, value is written raw (no CSV escaping) so Excel treats it as a formula
 *
 * rows: Array of plain objects (your data)
 */

function escapeCsvCell(value) {
  if (value == null) return '';
  const str = String(value);
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

export function exportToCsv(filename, columns, rows) {
  const header = columns.map((c) => escapeCsvCell(c.label)).join(',');
  const body = rows.map((row) =>
    columns
      .map((c) => {
        const val = c.transform ? c.transform(row) : row[c.key];
        // formula columns are written raw so Excel executes them (e.g. =IMAGE("url"))
        if (c.formula) return val == null ? '' : String(val);
        return escapeCsvCell(val);
      })
      .join(','),
  );

  // sep=, tells Excel to use comma as delimiter regardless of regional locale settings
  const csv = ['sep=,', header, ...body].join('\r\n');
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename.endsWith('.csv') ? filename : filename + '.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
