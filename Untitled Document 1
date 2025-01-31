function importCsvToGoogleSheet() {
  const sheetId = "1KuV1-7AUU3refg7fcGrKYfAmB14y3jUTin9o9iUjRQU";
  const sheetName = "SHERPA ERROR STATUS";
  const sender = "ati.alert@atimotors.com";  // Email remains same
  const subjects = ["Sherpa Errors", "Sherpa Error"];
  
  // Date setup for yesterday
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const dateStr = Utilities.formatDate(yesterday, Session.getScriptTimeZone(), "yyyy-MM-dd");

  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  let lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];

  // Check if "Error Count - [Date]" column already exists
  if (headers.includes(`Error Count - ${dateStr}`)) {
    Logger.log(`Column for Error Count - ${dateStr} is already present. No update needed.`);
    fillPreviousBlanks(sheet);
    return;
  }

  // Check if "Total Errors" is the last column; if so, remove it
  if (headers[lastColumn - 1] === "Total Errors") {
    sheet.deleteColumn(lastColumn);
    lastColumn -= 1;
  }

  // Create new columns for today's error count and total errors
  sheet.insertColumnAfter(lastColumn);
  sheet.getRange(1, lastColumn + 1).setValue(`Error Count - ${dateStr}`);
  lastColumn += 1;
  const errorCountColumnIndex = lastColumn;

  sheet.insertColumnAfter(lastColumn);
  sheet.getRange(1, lastColumn + 1).setValue("Total Errors");
  const totalErrorsColumnIndex = lastColumn + 1;

  // Search Gmail for the email
  const todayStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy/MM/dd");
  let threads = [];
  for (let subject of subjects) {
    threads = GmailApp.search(`subject:${subject} from:${sender} after:${todayStr}`);
    if (threads.length > 0) break;
  }

  if (threads.length === 0) {
    Logger.log("No matching email threads found.");
    setNoMailReceived(sheet, errorCountColumnIndex);
    fillPreviousBlanks(sheet);
    updateTotalErrors(sheet, totalErrorsColumnIndex);
    applyConditionalFormatting(sheet, errorCountColumnIndex, totalErrorsColumnIndex);
    return;
  }

  // Process attachments from the latest matching email
  const messages = threads.flatMap(thread => thread.getMessages());
  const attachments = messages[messages.length - 1].getAttachments();

  Logger.log(`Total attachments found: ${attachments.length}`);

  let csvData = null;
  attachments.forEach(attachment => {
    Logger.log(`Attachment Name: ${attachment.getName()} | Type: ${attachment.getContentType()}`);
    if (attachment.getName().toLowerCase() === "sherpa_errors.csv") { // Exact match
      csvData = Utilities.parseCsv(attachment.getDataAsString());
      Logger.log("Sherpa Errors CSV attachment found and parsed.");
    }
  });

  if (!csvData) {
    Logger.log("No valid CSV attachments found in the email.");
    setNoMailReceived(sheet, errorCountColumnIndex);
    fillPreviousBlanks(sheet);
    updateTotalErrors(sheet, totalErrorsColumnIndex);
    applyConditionalFormatting(sheet, errorCountColumnIndex, totalErrorsColumnIndex);
    return;
  }

  processCsvData(csvData, sheet, errorCountColumnIndex);
  fillPreviousBlanks(sheet);
  updateTotalErrors(sheet, totalErrorsColumnIndex);
  applyConditionalFormatting(sheet, errorCountColumnIndex, totalErrorsColumnIndex);
  sortSheet(sheet);
}

// Set "no mails received" if no email is found
function setNoMailReceived(sheet, errorCountColumnIndex) {
  const lastRow = sheet.getLastRow();
  const values = Array(lastRow - 1).fill(["no mails received"]);
  sheet.getRange(2, errorCountColumnIndex, lastRow - 1, 1).setValues(values);
}

// Fill blanks in previous error count columns with zero
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

// Process the CSV and update sheet
function processCsvData(data, sheet, errorCountColumnIndex) {
  const headers = data[0];
  const rows = data.slice(1);
  const sheetData = sheet.getDataRange().getValues();
  const lastRow = sheetData.length;

  const clientMap = new Map();
  for (let row = 1; row < lastRow; row++) {
    const key = `${sheetData[row][0]}|${sheetData[row][1]}|${sheetData[row][2]}`;
    clientMap.set(key, row);
    sheetData[row][errorCountColumnIndex - 1] = 0;
  }

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

  sheet.getRange(2, 1, sheetData.length - 1, sheetData[0].length).setValues(sheetData.slice(1));
}

// Update total errors column
function updateTotalErrors(sheet, totalErrorsColumnIndex) {
  const lastRow = sheet.getLastRow();
  const errorColumns = sheet.getRange(2, 4, lastRow - 1, totalErrorsColumnIndex - 4).getValues();

  const totalErrors = errorColumns.map(row => {
    return [row.reduce((sum, count) => sum + (parseInt(count, 10) || 0), 0)];
  });

  sheet.getRange(2, totalErrorsColumnIndex, lastRow - 1, 1).setValues(totalErrors);
}

// Apply conditional formatting
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

// Sort sheet data
function sortSheet(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).sort({ column: 1, ascending: true });
  }
}

