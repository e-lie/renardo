interface LogEntry {
    timestamp: string;
    level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
    component: string;
    message: string;
    data?: any;
}

class LoggerService {
    private logs: LogEntry[] = [];
    private maxLogs = 100;

    private createLogEntry(level: LogEntry['level'], component: string, message: string, data?: any): LogEntry {
        return {
            timestamp: new Date().toISOString(),
            level,
            component,
            message,
            data
        };
    }

    private addLog(entry: LogEntry) {
        // Add to local storage
        this.logs.push(entry);

        // Keep only the last maxLogs entries
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }

        // Console output
        const consoleMethod = entry.level === 'ERROR' ? 'error' :
            entry.level === 'WARN' ? 'warn' :
                entry.level === 'INFO' ? 'info' : 'debug';

        console[consoleMethod](`[${entry.component}] ${entry.message}`, entry.data || '');
    }

    debug(component: string, message: string, data?: any) {
        this.addLog(this.createLogEntry('DEBUG', component, message, data));
    }

    info(component: string, message: string, data?: any) {
        this.addLog(this.createLogEntry('INFO', component, message, data));
    }

    warn(component: string, message: string, data?: any) {
        this.addLog(this.createLogEntry('WARN', component, message, data));
    }

    error(component: string, message: string, data?: any) {
        this.addLog(this.createLogEntry('ERROR', component, message, data));
    }

    getLogs(): LogEntry[] {
        return [...this.logs];
    }

    clearLogs() {
        this.logs = [];
    }

    // Method to get logs for debugging
    exportLogs(): string {
        return JSON.stringify(this.logs, null, 2);
    }
}

// Export singleton instance
export const logger = new LoggerService();
export default logger;