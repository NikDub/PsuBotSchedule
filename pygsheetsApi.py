import pygsheets

from dbWork import *
from help import timeParse

gc = pygsheets.authorize(service_file="Data/creds.json", scopes=['https://www.googleapis.com/auth/spreadsheets',
                                                            'https://www.googleapis.com/auth/drive'])
sheets = gc.open_by_key("1ZSTYQ1cKa5fD8KYAdRmWlkzkvs35KGkqO-BKj8jZqBY")


def pygsheetsWrite():
    posDataFromFile = dataGet().fetchall()
    setStatus(posDataFromFile)
    for item in posDataFromFile:

        group = item[0]
        time = timeParse(item[1].strftime("%H:%M"))

        date = item[2].strftime("%d.%m.%Y")
        students = item[3].split('\n')
        sheet = sheets.worksheet_by_title(group)
        sheetData = sheet.get_all_values()

        dateColumn = 0
        timeColumn = 0

        countBreak = 0
        for columnDate in range(1, len(sheetData)):
            if sheetData[0][columnDate].strip() != "":
                if sheetData[0][columnDate].strip() == date:
                    dateColumn = columnDate
                temp = sheetData[0][columnDate].strip()
                countBreak = 0
            elif countBreak == 7:
                countBreak = 0
                if dateColumn == 0:
                    dateColumn = columnDate - 1
                    dateRange = sheet.get_values((1, dateColumn), (1, dateColumn + 5), returnas="range")
                    dateRange.update_values([[date]])
                    dateRange.merge_cells()
                    timeRange = sheet.get_values((2, dateColumn), (2, dateColumn + 5), returnas="range")
                    timeRange.update_values([["9:00", "10:30", "12:20", "13:50", "15:30", "17:00"]])
                    sheet.add_cols(7)
                break
            else:
                countBreak += 1

        sheetData = sheet.get_all_values()

        for columnTime in range(dateColumn, dateColumn + 6):
            if sheetData[1][columnTime].strip() != "":
                if sheetData[1][columnTime].strip() == time:
                    timeColumn = columnTime
                    break

        startIndex = 2
        for student in students:
            for rowStudent in range(startIndex, sheet.cols):
                temp = sheetData[rowStudent][0].strip()
                if temp != "":
                    if sheetData[rowStudent][0].strip().find(student.split(" ")[0]) != -1:
                        startIndex = rowStudent
                        if student[-1].lower() == "у" and student[-2] == " ":
                            sheet.cell((rowStudent + 1, timeColumn + 1)).value = "У"
                        else:
                            sheet.cell((rowStudent + 1, timeColumn + 1)).value = "2"
                        break
