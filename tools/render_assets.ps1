# Renders the favicon PNGs from favicon.svg and the social preview from tools/og.html.
# Run from PowerShell (Edge headless writes no file when started from Git Bash):
#   powershell -ExecutionPolicy Bypass -File tools\render_assets.ps1
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$root = Split-Path -Parent $PSScriptRoot
$tmp = Join-Path $root "tools\_cache"
New-Item -ItemType Directory -Force $tmp | Out-Null
$svgUrl = "file:///" + (($root -replace '\\','/') + "/favicon.svg")
foreach ($pair in @(@(180, "apple-touch-icon.png"), @(32, "favicon-32.png"))) {
  $n = $pair[0]
  $html = Join-Path $tmp "icon_$n.html"
  "<!doctype html><html><body style='margin:0;background:transparent'><img src='$svgUrl' width='$n' height='$n' style='display:block'></body></html>" | Out-File -Encoding utf8 $html
  & $edge --headless=new --disable-gpu --hide-scrollbars --default-background-color=00000000 --window-size="$n,$n" --screenshot="$root\$($pair[1])" ("file:///" + ($html -replace '\\','/')) 2>$null | Out-Null
}
& $edge --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=3000 --window-size=1200,630 --screenshot="$tmp\og.png" ("file:///" + ($root -replace '\\','/') + "/tools/og.html") 2>$null | Out-Null
Start-Sleep -Seconds 1
python -c "from PIL import Image; Image.open(r'$tmp\og.png').convert('RGB').save(r'$root\og-image.jpg', quality=86, optimize=True)"
Get-Item "$root\apple-touch-icon.png", "$root\favicon-32.png", "$root\og-image.jpg" | Select-Object Name, Length
