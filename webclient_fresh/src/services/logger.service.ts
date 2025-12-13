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
    private urqlClient: any = null;

    constructor() {
        // Try to get URQL client from context
        this.initializeClient();
    }

    private initializeClient() {
        // Import getClient dynamically to avoid SSR issues
        import('@urql/svelte').then(({ getContextClient }) => {
            try {
                this.urqlClient = getContextClient();
            } catch (error) {
                // Client not available, will use console only
                console.warn('[LoggerService] URQL client not available, using console only');
            }
        }).catch(() => {
            // Module not available, will use console only
        });
    }

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

        // Send to backend if available
        this.sendToBackend(entry);
    }

    private async sendToBackend(entry: LogEntry) {
        if (!this.urqlClient) return;

        try {
            // Import the mutation dynamically
            import('../api-client/graphql/queries').then(({ SEND_FRONTEND_LOG }) => {
                const variables = {
                    timestamp: entry.timestamp,
                    level: entry.level,
                    component: entry.component,
                    message: entry.message,
                    data: entry.data ? JSON.stringify(entry.data) : null
                };

                this.urqlClient.mutation(SEND_FRONTEND_LOG, variables).toPromise().then((result: any) => {
                    if (result.error) {
                        console.warn('[LoggerService] Failed to send log to backend:', result.error);
                    }
                }).catch((error: any) => {
                    console.warn('[LoggerService] Failed to send log to backend:', error);
                });
            }).catch((error: any) => {
                console.warn('[LoggerService] Failed to import queries:', error);
            });
        } catch (error) {
            // Silently fail to avoid infinite loops
            console.warn('[LoggerService] Failed to send log to backend:', error);
        }
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