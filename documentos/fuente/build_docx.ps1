# Construye el informe .docx del proyecto de A* a partir de contenido.txt, codigo.txt y img/.
# Escribe el paquete Office Open XML directamente: NO necesita Word instalado ni abierto.
# No contiene rutas absolutas: resuelve su ubicacion con $PSScriptRoot.
# Uso:  powershell -ExecutionPolicy Bypass -File build_docx.ps1

Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$base    = $PSScriptRoot
$imgDir  = Join-Path $base 'img'
# El nombre de salida se puede pasar como primer argumento;
# sin argumento usa el de siempre.
$nombreSalida = if ($args.Count -ge 1 -and $args[0]) { $args[0] } else { 'Informe Tecnico Algoritmo A-estrella.docx' }
$outFile = Join-Path $base $nombreSalida
$work    = Join-Path $env:TEMP ('docxbuild_' + [guid]::NewGuid().ToString('N'))

$EMU_PER_INCH = 914400

function Esc([string]$s) {
    $s = $s -replace '&', '&amp;'
    $s = $s -replace '<', '&lt;'
    $s = $s -replace '>', '&gt;'
    return $s
}

# ---- lectura del contenido -------------------------------------------------
$lines = Get-Content -LiteralPath (Join-Path $base 'contenido.txt') -Encoding UTF8

$imgRels  = @()   # @{ id; file; src }
$imgCount = 0
$body     = New-Object System.Text.StringBuilder

function Add-Para {
    param(
        [string]$text,
        [int]$sizeHalfPt = 20,
        [int]$afterTwips = 80,
        [int]$beforeTwips = 0,
        [string]$align = 'left',
        [bool]$bold = $false,
        [bool]$italic = $false,
        [string]$font = 'Times New Roman',
        [string]$fill = '',
        [int]$indentTwips = 0
    )
    $pPr = '<w:pPr>'
    if ($fill -ne '') { $pPr += '<w:shd w:val="clear" w:color="auto" w:fill="' + $fill + '"/>' }
    if ($indentTwips -gt 0) { $pPr += '<w:ind w:left="' + $indentTwips + '" w:right="' + $indentTwips + '"/>' }
    $pPr += '<w:spacing w:before="' + $beforeTwips + '" w:after="' + $afterTwips + '" w:line="240" w:lineRule="auto"/>'
    if ($align -ne 'left') { $pPr += '<w:jc w:val="' + $align + '"/>' }
    $pPr += '</w:pPr>'

    $rPr = '<w:rPr><w:rFonts w:ascii="' + $font + '" w:hAnsi="' + $font + '" w:cs="' + $font + '"/>'
    if ($bold)   { $rPr += '<w:b/>' }
    if ($italic) { $rPr += '<w:i/>' }
    $rPr += '<w:sz w:val="' + $sizeHalfPt + '"/><w:szCs w:val="' + $sizeHalfPt + '"/></w:rPr>'

    $run = ''
    if ($text -ne '') {
        $run = '<w:r>' + $rPr + '<w:t xml:space="preserve">' + (Esc $text) + '</w:t></w:r>'
    }
    return '<w:p>' + $pPr + $run + '</w:p>'
}

foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $idx = $line.IndexOf('|')
    if ($idx -lt 0) { continue }
    $tag     = $line.Substring(0, $idx)
    $payload = $line.Substring($idx + 1)

    switch ($tag) {

        'H1' { [void]$body.Append((Add-Para -text $payload -sizeHalfPt 30 -afterTwips 40 -align 'center' -bold $true)) }

        'SUB' { [void]$body.Append((Add-Para -text $payload -sizeHalfPt 20 -afterTwips 180 -align 'center')) }

        'META' {
            $p = $payload.Split('|')
            $rPrB = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr>'
            $rPrN = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr>'
            $xml  = '<w:p><w:pPr><w:spacing w:before="0" w:after="20" w:line="240" w:lineRule="auto"/></w:pPr>'
            $xml += '<w:r>' + $rPrB + '<w:t xml:space="preserve">' + (Esc ($p[0] + ' ')) + '</w:t></w:r>'
            $xml += '<w:r>' + $rPrN + '<w:t xml:space="preserve">' + (Esc $p[1]) + '</w:t></w:r></w:p>'
            [void]$body.Append($xml)
        }

        'H2' { [void]$body.Append((Add-Para -text $payload -sizeHalfPt 23 -beforeTwips 180 -afterTwips 60 -bold $true)) }

        'P'  { [void]$body.Append((Add-Para -text $payload)) }

        'CAP' { [void]$body.Append((Add-Para -text $payload -sizeHalfPt 16 -afterTwips 140 -italic $true)) }

        'IMGROW' {
            $parts   = $payload.Split('|')
            $files   = $parts[0].Split(';')
            $widthIn = [double]$parts[1]
            $runs    = ''
            foreach ($f in $files) {
                $path = Join-Path $imgDir $f
                if (-not (Test-Path $path)) { Write-Output ("FALTA imagen: " + $f); continue }
                $imgCount++
                $relId   = 'rIdImg' + $imgCount
                $newName = 'image' + $imgCount + [System.IO.Path]::GetExtension($f)
                $imgRels += @{ id = $relId; file = $newName; src = $path }

                $dec = [System.Windows.Media.Imaging.BitmapDecoder]::Create(
                         (New-Object System.Uri($path)), 'None', 'OnLoad')
                $pw  = $dec.Frames[0].PixelWidth
                $ph  = $dec.Frames[0].PixelHeight
                $cx  = [int]($widthIn * $EMU_PER_INCH)
                $cy  = [int]($widthIn * ($ph / $pw) * $EMU_PER_INCH)

                $runs += '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
                $runs += '<wp:extent cx="' + $cx + '" cy="' + $cy + '"/>'
                $runs += '<wp:docPr id="' + $imgCount + '" name="Imagen ' + $imgCount + '"/>'
                $runs += '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                $runs += '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                $runs += '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                $runs += '<pic:nvPicPr><pic:cNvPr id="' + $imgCount + '" name="' + $newName + '"/><pic:cNvPicPr/></pic:nvPicPr>'
                $runs += '<pic:blipFill><a:blip r:embed="' + $relId + '"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                $runs += '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="' + $cx + '" cy="' + $cy + '"/></a:xfrm>'
                $runs += '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
                $runs += '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
                if ($f -ne $files[$files.Count - 1]) {
                    $runs += '<w:r><w:t xml:space="preserve"> </w:t></w:r>'
                }
            }
            [void]$body.Append('<w:p><w:pPr><w:spacing w:before="0" w:after="40" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>' + $runs + '</w:p>')
        }

        'CODEFILE' {
            $code = Get-Content -LiteralPath (Join-Path $base $payload) -Encoding UTF8
            for ($k = 0; $k -lt $code.Count; $k++) {
                [void]$body.Append((Add-Para -text $code[$k] -sizeHalfPt 12 -afterTwips 0 `
                                    -font 'Consolas' -fill 'F2F2F2' -indentTwips 90))
            }
            [void]$body.Append((Add-Para -text '' -afterTwips 60))
        }

        'PAGEBREAK' {
            [void]$body.Append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        }
    }
}

# ---- sectPr: carta, margenes ----------------------------------------------
$sect  = '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
$sect += '<w:pgMar w:top="864" w:right="1008" w:bottom="864" w:left="1008" w:header="720" w:footer="720" w:gutter="0"/>'
$sect += '</w:sectPr>'

$docXml  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "`r`n"
$docXml += '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
$docXml += 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
$docXml += 'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
$docXml += '<w:body>' + $body.ToString() + $sect + '</w:body></w:document>'

# ---- relaciones ------------------------------------------------------------
$relsDoc  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "`r`n"
$relsDoc += '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
$relsDoc += '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
foreach ($r in $imgRels) {
    $relsDoc += '<Relationship Id="' + $r.id + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/' + $r.file + '"/>'
}
$relsDoc += '</Relationships>'

$rootRels  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "`r`n"
$rootRels += '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
$rootRels += '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
$rootRels += '</Relationships>'

$styles  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "`r`n"
$styles += '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
$styles += '<w:docDefaults><w:rPrDefault><w:rPr>'
$styles += '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
$styles += '<w:sz w:val="20"/><w:szCs w:val="20"/><w:lang w:val="es-DO"/>'
$styles += '</w:rPr></w:rPrDefault>'
$styles += '<w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
$styles += '</w:docDefaults>'
$styles += '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
$styles += '</w:styles>'

$ct  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "`r`n"
$ct += '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
$ct += '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
$ct += '<Default Extension="xml" ContentType="application/xml"/>'
$ct += '<Default Extension="png" ContentType="image/png"/>'
$ct += '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
$ct += '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
$ct += '</Types>'

# ---- empaquetado -----------------------------------------------------------
# Las entradas del ZIP deben usar '/' (nunca '\'), o Word rechaza el archivo.
$utf8 = New-Object System.Text.UTF8Encoding($false)

if (Test-Path $outFile) { Remove-Item $outFile -Force }
$fs  = [System.IO.File]::Open($outFile, 'Create')
$zip = New-Object System.IO.Compression.ZipArchive($fs, 'Create')

function Add-TextEntry($zip, $name, $text, $enc) {
    $entry  = $zip.CreateEntry($name, 'Optimal')
    $stream = $entry.Open()
    $bytes  = $enc.GetBytes($text)
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Close()
}

function Add-FileEntry($zip, $name, $path) {
    $entry  = $zip.CreateEntry($name, 'Optimal')
    $stream = $entry.Open()
    $bytes  = [System.IO.File]::ReadAllBytes($path)
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Close()
}

Add-TextEntry $zip '[Content_Types].xml'          $ct       $utf8
Add-TextEntry $zip '_rels/.rels'                  $rootRels $utf8
Add-TextEntry $zip 'word/document.xml'            $docXml   $utf8
Add-TextEntry $zip 'word/_rels/document.xml.rels' $relsDoc  $utf8
Add-TextEntry $zip 'word/styles.xml'              $styles   $utf8
foreach ($r in $imgRels) { Add-FileEntry $zip ('word/media/' + $r.file) $r.src }

$zip.Dispose()
$fs.Close()

Write-Output ("Generado: " + $outFile)
Write-Output ("Imagenes embebidas: " + $imgCount)

