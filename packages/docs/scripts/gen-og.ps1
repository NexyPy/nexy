# Generates assets/og.png (1200x630 social share card) for the Nexy docs.
# Run:  pwsh ./scripts/gen-og.ps1   (needs System.Drawing, Windows-only)
Add-Type -AssemblyName System.Drawing

$W = 1200; $H = 630
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

# Background (dark-first brand #09160D)
$g.Clear([System.Drawing.Color]::FromArgb(9, 22, 13))

# Brand gradient bar (teal -> blue) on the left edge
$brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
  (New-Object System.Drawing.Rectangle(0, 0, 10, $H)),
  [System.Drawing.Color]::FromArgb(0, 208, 132),
  [System.Drawing.Color]::FromArgb(97, 171, 237),
  90.0)
$g.FillRectangle($brush, 0, 0, 10, $H)

# Headline "Nexy"
$white = [System.Drawing.Color]::FromArgb(242, 247, 244)
$gray  = [System.Drawing.Color]::FromArgb(165, 182, 174)
$green = [System.Drawing.Color]::FromArgb(77, 224, 128)
$br  = New-Object System.Drawing.SolidBrush($green)
$brh = New-Object System.Drawing.SolidBrush($white)
$brg = New-Object System.Drawing.SolidBrush($gray)

$fn1 = [System.Drawing.Font]::new("Segoe UI", 96, [System.Drawing.FontStyle]::Bold)
$g.DrawString("Nexy", $fn1, $br, 96, 140)
$fn1.Dispose()

# Tagline
$fn2 = [System.Drawing.Font]::new("Segoe UI", 30, [System.Drawing.FontStyle]::Regular)
$g.DrawString("New eXperience for PYthon", $fn2, $brh, 102, 300)
$g.DrawString("Python for the modern web, reimagined", $fn2, $brg, 102, 360)
$fn2.Dispose()

# Footer pill
$fn3 = [System.Drawing.Font]::new("Segoe UI", 18, [System.Drawing.FontStyle]::Regular)
$g.DrawString("nexy.dev  ·  full-stack framework on FastAPI", $fn3, $brg, 102, 520)
$fn3.Dispose()

$g.Dispose()
$bmp.Save("$PSScriptRoot/../assets/og.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "og.png written"