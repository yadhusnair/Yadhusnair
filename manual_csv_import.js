function manualImportCsv() {
  const sheetId = "1KuV1-7AUU3refg7fcGrKYfAmB14y3jUTin9o9iUjRQU";
  const sheetName = "SHERPA ERROR STATUS";
  const fileName = "sherpa_errors.csv"; // Change this if your file has a different name

  // Fetch file from Google Drive
  const folder = DriveApp.getFoldersByName("Sherpa CSV Uploads").next(); // Ensure the folder exists
  const files = folder.getFilesByName(fileName);
  if (!files.hasNext()) {
    Logger.log("No CSV file found in the folder.");
    return;
  }

  const file = files.next();
  const csvData = Utilities.parseCsv(file.getBlob().getDataAsString());

  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  const lastColumn = sheet.getLastColumn();
  const lastRow = sheet.getLastRow();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];

  // Prompt for date input
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt("Enter the date for this CSV (YYYY-MM-DD):");
  if (response.getSelectedButton() !== ui.Button.OK) return;
  const dateStr = response.getResponseText();

  // Check if the column for the date exists
  let errorCountColumnIndex = headers.indexOf(`Error Count - ${dateStr}`) + 1;
  if (errorCountColumnIndex === 0) {
    sheet.insertColumnAfter(lastColumn);
    sheet.getRange(1, lastColumn + 1).setValue(`Error Count - ${dateStr}`);
    errorCountColumnIndex = lastColumn + 1;
  }

  processCsvData(csvData, sheet, errorCountColumnIndex);
  fillPreviousBlanks(sheet);
  updateTotalErrors(sheet, lastColumn + 2);
  applyConditionalFormatting(sheet, errorCountColumnIndex, lastColumn + 2);
  sortSheet(sheet);
}

// 🛠 Process the CSV and update sheet
function processCsvData(data, sheet, errorCountColumnIndex) {
  const headers = data[0]; // CSV headers
  const rows = data.slice(1); // CSV data (excluding headers)
  const sheetData = sheet.getDataRange().getValues();
  const lastRow = sheetData.length;

  // Create a map to track existing client, entity, and error code
  const clientMap = new Map();
  for (let row = 1; row < lastRow; row++) {
    const key = `${sheetData[row][0]}|${sheetData[row][1]}|${sheetData[row][2]}`;
    clientMap.set(key, row);
    sheetData[row][errorCountColumnIndex - 1] = 0; // Initialize with 0
  }

  // Loop through CSV rows and update the sheet
  rows.forEach(row => {
    const [fm_client, entity_name, type, code, error_count] = row;
    if (type !== "mule_error") return;

    const key = `${fm_client}|${entity_name}|${code}`;
    const errorValue = parseInt(error_count, 10) || 0;

    if (clientMap.has(key)) {
      const sheetRow = clientMap.get(key);
      sheetData[sheetRow][errorCountColumnIndex - 1] = errorValue;
    } else {
      const newRow = Array(sheetData[0].length).fill("");
      newRow[0] = fm_client;
      newRow[1] = entity_name;
      newRow[2] = code;
      newRow[errorCountColumnIndex - 1] = errorValue;
      sheetData.push(newRow);
    }
  });

  // Update the sheet with modified values
  sheet.getRange(2, 1, sheetData.length - 1, sheetData[0].length).setValues(sheetData.slice(1));
}

// 🛠 Fill blanks in previous error count columns with zero
function fillPreviousBlanks(sheet) {
  const lastRow = sheet.getLastRow();
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];

  headers.forEach((header, colIndex) => {
    if (header.startsWith("Error Count -")) {
      const range = sheet.getRange(2, colIndex + 1, lastRow - 1);
      const values = range.getValues();
      for (let i = 0; i < values.length; i++) {
        if (values[i][0] === "" || values[i][0] == null) {
          values[i][0] = 0;
        }
      }
      range.setValues(values);
    }
  });
}

// 🛠 Update total errors column
function updateTotalErrors(sheet, totalErrorsColumnIndex) {
  const lastRow = sheet.getLastRow();
  const errorColumns = sheet.getRange(2, 4, lastRow - 1, totalErrorsColumnIndex - 4).getValues();

  const totalErrors = errorColumns.map(row => {
    return [row.reduce((sum, count) => sum + (parseInt(count, 10) || 0), 0)];
  });

  sheet.getRange(2, totalErrorsColumnIndex, lastRow - 1, 1).setValues(totalErrors);
}

// 🛠 Apply conditional formatting
function applyConditionalFormatting(sheet, errorCountColumnIndex, totalErrorsColumnIndex) {
  const lastRow = sheet.getLastRow();
  sheet.clearConditionalFormatRules();

  const errorCountRange = sheet.getRange(2, 4, lastRow - 1, errorCountColumnIndex - 3);
  const errorCountRedRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThanOrEqualTo(5)
    .setBackground("#E06666")
    .setRanges([errorCountRange])
    .build();

  sheet.setConditionalFormatRules([errorCountRedRule]);
}

// 🛠 Sort sheet data
function sortSheet(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).sort({ column: 1, ascending: true });
  }
}

