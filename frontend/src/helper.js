export function getCurrencyText(cost, currency = 'GBP') {
    if (cost == null || currency == null) {
        return "-"
    }
    var formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    });
    return formatter.format(cost);
}

export function timeToDate(str) {
    let newTime = new Date()
    newTime.setHours(str.split(":")[0])
    newTime.setMinutes(str.split(":")[1])
    return newTime
}

export function getScheduleRatio(vm) {
    if (vm.stopTime == null || vm.startTime == null) {
        return null
    }
    let stopTime = timeToDate(vm.stopTime)
    let startTime = timeToDate(vm.startTime)

    let diffMs = stopTime - startTime
    let diffMins = Math.floor((diffMs / 1000) / 60)

    // Count number of days running
    let dayCount = 0
    Object.keys(vm.daysOfWeek).forEach(function (value) {
        if (vm.daysOfWeek[value]) {
            dayCount += 1
        }
    })
    return (diffMins / 1440) * (dayCount / 7)
}

export function getScheduleStr(data) {
    let chunks = []
    let currentChunk = []
    Object.keys(data).forEach(function (value) {
        if (data[value] == true) {
            currentChunk.push(value)
        } else {
            if (currentChunk.length > 0) {
                chunks.push(currentChunk)
                currentChunk = []
            }
        }

        if (value == "Sun" && currentChunk.length > 0) {
            chunks.push(currentChunk)
        }
    })
    
    let outputStr = ""
    chunks.forEach(function (value) {
        if (value.length < 3) {
            // Comma seperated
            outputStr += value.join(",")
        } else {
            // Dash seperated
            outputStr += `${value[0]}-${value[value.length - 1]}`
        }

        outputStr += ","
    })
    // Remove last comma
    return outputStr.slice(0, -1)
}