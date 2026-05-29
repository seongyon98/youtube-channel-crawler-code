# Set Working Directory
Set-Location $PSScriptRoot

# --- Duplicate Run Prevention (Lock File) ---
$LOCK_FILE = "$PSScriptRoot/.crawler.lock"
if (Test-Path $LOCK_FILE) {
    $old_pid = Get-Content $LOCK_FILE -ErrorAction SilentlyContinue
    if ($old_pid -and (Get-Process -Id $old_pid -ErrorAction SilentlyContinue)) {
        Write-Host "⚠️ 이미 다른 크롤러 인스턴스(PID: $old_pid)가 실행 중입니다." -ForegroundColor Yellow
        Write-Host "중복 실행을 방지하기 위해 이 창을 종료합니다." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        exit 0
    }
}
$PID | Out-File -FilePath $LOCK_FILE -Encoding UTF8 -Force

# --- Logging Start ---
$LOG_DIR = "$PSScriptRoot/logs"
if (!(Test-Path $LOG_DIR)) { New-Item -Path $LOG_DIR -ItemType Directory | Out-Null }
$LOG_FILE = "$LOG_DIR/crawler_run.log"
Start-Transcript -Path $LOG_FILE -Append -Force
# ---------------------

try {
    # Encoding Fix
    $OutputEncoding = [System.Text.Encoding]::UTF8

    # [FORCE SYNC] Fetch latest from origin and hard-reset to origin/feature/openai-filter
    # This works regardless of which branch or state the local repo is in.
    Write-Host "Force-syncing to origin/feature/openai-filter..."
    git fetch origin feature/openai-filter --prune --quiet
    git checkout -B feature/openai-filter origin/feature/openai-filter
    Write-Host "Now on feature/openai-filter, synced with origin/feature/openai-filter."

    # [ULTIMATE ENCODING FIX] Read name from a separate text file
    $NAME_FILE = "$PSScriptRoot/my_name.txt"
    if (Test-Path $NAME_FILE) {
        $USER_NAME = (Get-Content $NAME_FILE -Encoding UTF8).Trim()
    }
    else {
        $USER_NAME = "NAME_HERE"
    }

    # [PRODUCTION SETTING] Target Branch
    $TARGET_BRANCH = "feature/openai-filter"

    # [Date Extract] YYMMDD
    $full_date = Get-Date -Format "yyMMdd"

    Write-Host "Pulling latest data from origin/main..."
    git pull --rebase origin $TARGET_BRANCH

    Write-Host "Checking and installing required libraries..."
    pip install -r requirements.txt -q

    Write-Host "Starting Crawler..."
    python youtube_channel_crawler.py --auto

    Write-Host "Uploading to GitHub..."
    git add data/*.json

    # Commit Message with Computer and User info
    $KOREAN_DONE = [char]0xC218 + [char]0xC9D1 + [char]0xC644 + [char]0xB8CC
    $pc_info = "$env:COMPUTERNAME\$env:USERNAME"
    $commit_msg = "${full_date}_${USER_NAME}_${KOREAN_DONE} ${pc_info}"
    git commit -m "$commit_msg"

    # Push with retry
    $MAX_RETRY = 3
    $pushed = $false
    for ($i = 1; $i -le $MAX_RETRY; $i++) {
        Write-Host "Push attempt $i / $MAX_RETRY ..."
        git push origin "$TARGET_BRANCH"
        if ($LASTEXITCODE -eq 0) {
            $pushed = $true
            break
        }
        Write-Host "Push failed. Pulling latest changes and retrying..."
        git pull --rebase origin "$TARGET_BRANCH"
    }

    if ($pushed) {
        Write-Host "All tasks completed successfully!"
    }
    else {
        Write-Host "ERROR: Push failed after $MAX_RETRY attempts. Please push manually."
        exit 1
    }
}
finally {
    # Remove Lock File
    if (Test-Path $LOCK_FILE) {
        $stored_pid = Get-Content $LOCK_FILE -ErrorAction SilentlyContinue
        if ($stored_pid -eq $PID) {
            Remove-Item $LOCK_FILE -Force -ErrorAction SilentlyContinue
        }
    }
    # --- Logging End ---
    Stop-Transcript
}

