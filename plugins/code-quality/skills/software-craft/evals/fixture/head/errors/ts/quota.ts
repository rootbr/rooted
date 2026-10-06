export interface Account {
  id: string;
  used: number;
  limit: number;
}

export function reserveQuotaThrowsString(account: Account, units: number): void {
  if (account.used + units > account.limit) {
    throw `quota exceeded for account ${account.id}: ${account.used + units} of ${account.limit} units`;
  }
  account.used += units;
}

export function renderQuotaBannerThrowsPlainError(template: string, account: Account): string {
  if (!template.includes("{remaining}")) {
    // no caller tells this failure apart from others: it surfaces as a bug report with its stack trace
    throw new Error(`render quota banner for account ${account.id}: template lacks {remaining}`);
  }
  return template.replace("{remaining}", String(account.limit - account.used));
}
