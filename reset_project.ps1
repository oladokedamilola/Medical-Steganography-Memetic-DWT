# ============================================
# FILE: reset_project.ps1
# ============================================

Write-Host "🧹 Cleaning old results..." -ForegroundColor Yellow

# Delete experiment results
if (Test-Path "data/experiment_results") {
    Remove-Item -Path "data/experiment_results" -Recurse -Force
    Write-Host "  ✅ Deleted data/experiment_results"
}

# Delete generated tables
if (Test-Path "results/tables") {
    Remove-Item -Path "results/tables/*" -Recurse -Force
    Write-Host "  ✅ Cleaned results/tables"
}

# Delete generated graphs
if (Test-Path "results/graphs") {
    Remove-Item -Path "results/graphs/*" -Recurse -Force
    Write-Host "  ✅ Cleaned results/graphs"
}

# Delete old histograms
if (Test-Path "figures") {
    Remove-Item -Path "figures/*.png" -Force
    Write-Host "  ✅ Cleaned figures/"
}

# Delete old summary
if (Test-Path "results/results_summary.txt") {
    Remove-Item -Path "results/results_summary.txt" -Force
    Write-Host "  ✅ Deleted results_summary.txt"
}

# Delete progress file (to start fresh)
if (Test-Path "data/experiment_results/progress.json") {
    Remove-Item -Path "data/experiment_results/progress.json" -Force
    Write-Host "  ✅ Deleted progress.json"
}

Write-Host "`n✅ Cleanup complete! Ready for fresh experiments." -ForegroundColor Green