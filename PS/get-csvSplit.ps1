function get-csvSplit
{
    [CmdletBinding()]
    Param(
        # file name without extension
        [Parameter(Mandatory=$true, Position=1)]
        $fileName,
        [Parameter(Mandatory=$true, Position=2)]
        $splitProperty,
        [Parameter(Mandatory=$false)]
        $propertyValue="",
        [switch]$preScan=$true
    )

    # appending arrays in powershell with += isn't efficient because it actually creates a new array.
    # use a list instead.
    [System.Collections.Generic.List[string]]$fileLines = new-object System.Collections.Generic.List[string]

    # we cannot read the file all at once because it is too large to fit in memory
    try {
        $reader = new-object System.IO.StreamReader(($fileName+".csv"))        
    }
    catch 
    {
        throw "$_", "could not open file $fileName .csv -- please provide the file name without the extension (temp hack)"
    }

    $fileLines = @()

    $outFileCount = 0

    $totalLines = 0
    $tmp = ""
    if ( $preScan )
    {
        while ( $tmp -ne $null )
        {
            $tmp = $reader.ReadLine()
            $totalLines++

            if ( $totalLines % 100000 -eq 0)
            {
                Write-debug "prescan at line $totalLines..."
            }
        }
    }

    Write-Verbose "prescan done, found $totalLines lines"

    $reader.Dispose()
    $reader = new-object System.IO.StreamReader(($fileName+".csv"))

    [switch]$foundNonCommentLine = $false
    # read the property line from the file
    while (-not $foundNonCommentLine) {
        $propLine = $reader.ReadLine()
        if ( -not $propLine.StartsWith("#"))
        {
            $foundNonCommentLine = $true
        }
    }

    [array]$propNames = $propLine.Split(",")

    write-debug "The prop line is $propLine"

    $propIndex = -1

    for ($p = 0; $p -lt $propNames.Count; $p++) {
        $prop = $propNames[$p]
        if ( $prop -eq $splitProperty )
        {
            $propIndex = $p
            break
        }
    }

    write-debug "The property index is $propIndex"

    if ( $propIndex -eq -1 )
    {
        throw "File $fileName does not contain the splitProperty $splitProperty"
    }

    $lastTestProperty = ""
    [array]$fileLineArray

    $filePercent = "?"
    $inFileLineNumber = 1
    $outFileLineCount = 0
    do {
        $fileLine = $reader.ReadLine()

        if ( $fileLine -eq $null )
        {
            break
        }

        $inFileLineNumber++
        
        $fileLineArray = $fileLine.Split(",")
        if ( $fileLines.Count -gt 0 -and $lastTestProperty -ne $fileLineArray[$propIndex])
        {
            if ( $propertyValue.Length -eq 0 -or $lastTestProperty -eq $propertyValue )
            {
                # write the file containing the current context                
                $outFile = ($fileName + "_" + $lastTestProperty + ".csv")
                if ( $totalLines -gt 0)
                {
                    $filePercent = "{0:0.0}" -f ($inFileLineNumber/$totalLines*100.0)
                }
                write-verbose "at file line $inFileLineNumber (${filePercent}%), Writing $outFile, $($fileLines.Count) lines"
                $fileLines.ToArray() | out-file $outFile

                $outFileCount++
                $totaloutFileLines += $fileLines.Count

                # start a new buffer of output lines
                [System.Collections.Generic.List[string]]$fileLines = new-object System.Collections.Generic.List[string]
                # put the property line on the new file to be written
                $fileLines.Add($propLine)
                $outFileLineCount = 1
            }
            else 
            {
                if ( $totalLines -gt 0)
                {
                    $filePercent = "{0:0.0}" -f ($inFileLineNumber/$totalLines*100.0)
                }
                Write-Verbose "at file line $inFileLineNumber (${filePercent}%), skipping $splitProperty $lastTestProperty because it doesn't match $splitProperty $propertyValue"

                [System.Collections.Generic.List[string]]$fileLines = new-object System.Collections.Generic.List[string]
                # put the property line on the new file to be written
                $fileLines.Add($propLine)
                $outFileLineCount = 1
            }
        }

        $fileLines.Add($fileLine)

        $outFileLineCount++
        $lastTestProperty = $fileLineArray[$propIndex]

        if ( $inFileLineNumber -gt 0 -and ($inFileLineNumber % 100000 -eq 0))
        {
            if ( $totalLines -gt 0 )
            {
                $filePercent = "{0:0.0}" -f ($inFileLineNumber/$totalLines*100.0)
            }
            Write-Verbose "at file line $inFileLineNumber (${filePercent}%), scanning $splitProperty $lastTestProperty, $outFileLineCount lines so far ..."
        }
    } until ( $fileLine -eq $null )

    if ( $propertyValue.Length -eq 0 -or $propertyValue -eq $lastTestProperty )
    {
# write the last file containing the leftover context
        $outFile = ($fileName + "_" + $lastTestProperty + ".csv")
        write-verbose "reached EOF at line $inFileLineNumber (100%), Writing last file $outFile, $($fileLines.Count) lines"
        $fileLines.ToArray() | out-file $outFile

        $outFileCount++
        $totaloutFileLines += $fileLines.Count
    }
    else 
    {
        Write-Verbose "at file line $inFileLineNumber (100%), skipping $splitProperty $lastTestProperty because it doesn't match $splitProperty $propertyValue"
    }

    Write-Verbose "For file $($fileName+'.csv'), $totalLines lines, $outFileCount files written, totaling $totaloutFileLines lines"

    $reader.Dispose()
}