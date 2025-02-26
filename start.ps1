# --- INITIAL SETUP ---
Write-Host "Initializing Dota 2 Patch Notes Assistant..." -ForegroundColor Cyan

# Get the script's directory dynamically
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Project Path: $projectPath"

# Paths and Commands
$listPatchnotesCSV = Join-Path -Path $projectPath -ChildPath "data\patchnotes\list_patchnotes.csv"
$pythonCmd = "python"
$appCmd = "$pythonCmd -m src.api.app"

# --- FETCH LATEST PATCH ---

# Function to get the latest patch version from the Dota 2 API
function Get-LatestPatch {
  Write-Host "Fetching the latest patch version from Dota 2 API..." -ForegroundColor Yellow
  $url = "https://www.dota2.com/datafeed/patchnoteslist?language=english"

  try {
      # Send request to API
      $response = Invoke-RestMethod -Uri $url -Method Get
      Write-Host "API Response received." -ForegroundColor Green

      # Ensure response and patches exist
      if ($response -and $response.patches) {
          # Get the latest patch from the patches array
          $latestPatch = $response.patches[-1].patch_name  # Use 'patch_name' field
          $patchTimestamp = $response.patches[-1].patch_timestamp  # Optional: Timestamp

          # Display the result
          Write-Host "Latest Patch from API: $latestPatch (Timestamp: $patchTimestamp)" -ForegroundColor Green
          return $latestPatch
      }
      else {
          # Handle missing or empty patches
          Write-Host "No patches found in the API response." -ForegroundColor Red
          exit 1
      }
  } catch {
      # Handle errors gracefully
      Write-Host "Failed to fetch latest patch. Error: $_" -ForegroundColor Red
      exit 1
  }
}


# --- READ CURRENT PATCHES ---

# Function to get the current patch versions from CSV
function Get-CurrentPatches {
    Write-Host "Reading current patches from $listPatchnotesCSV..." -ForegroundColor Yellow
    if (-Not (Test-Path $listPatchnotesCSV)) {
        Write-Host "Patchnotes CSV not found! ($listPatchnotesCSV)" -ForegroundColor Red
        exit 1
    }

    $patches = Import-Csv -Path $listPatchnotesCSV | Select-Object -ExpandProperty patch
    Write-Host "Current patches: $($patches -join ', ')" -ForegroundColor Green
    return $patches
}

# --- CHECK FOR PATCH UPDATES ---

$latestPatch = Get-LatestPatch
$currentPatches = Get-CurrentPatches

if ($latestPatch -in $currentPatches) {
    Write-Host "Latest patch ($latestPatch) already exists locally. Skipping update!" -ForegroundColor Green
} else {
    Write-Host "New patch detected ($latestPatch)! Updating patch notes..." -ForegroundColor Magenta

    # --- APPEND THE LATEST PATCH
     Write-Host "Appending new patch ($latestPatch) to list_patchnotes.csv..." -ForegroundColor Yellow
     Add-Content -Path $listPatchnotesCSV -Value "`n$latestPatch"
     Write-Host "Patch ($latestPatch) added to list_patchnotes.csv!" -ForegroundColor Green

    # --- RUN UPDATE SCRIPTS ---
    Write-Host "Downloading patch notes..." -ForegroundColor Yellow
    & $pythonCmd -m src.init_setup.download_patch_notes
    Write-Host "Patch notes downloaded!" -ForegroundColor Green

    Write-Host "Fetching mappers..." -ForegroundColor Yellow
    & $pythonCmd -m src.init_setup.fetch_mappers
    Write-Host "Mappers fetched!" -ForegroundColor Green

    Write-Host "Modifying patch notes..." -ForegroundColor Yellow
    & $pythonCmd -m src.init_setup.modify_patch_notes
    Write-Host "Patch notes modified!" -ForegroundColor Green

    Write-Host "Updating vector store..." -ForegroundColor Yellow
    & $pythonCmd -m src.vectorstore.add_to_vectorstore
    Write-Host "Vector store updated!" -ForegroundColor Green

    Write-Host "Update complete!" -ForegroundColor Cyan
}

# --- LAUNCH THE APP ---
Write-Host "Starting the Dota 2 Patch Notes Assistant..." -ForegroundColor Cyan
Invoke-Expression $appCmd
