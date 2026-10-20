import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'utcToLocal',
})
export class UtcToLocalPipe implements PipeTransform {
  transform(utc: string | null | undefined): string {
    if (!utc) {
      return '';
    }

    const hasZone = /(?:Z|[+-]\d{2}:\d{2})$/.test(utc);
    const parsed = new Date(hasZone ? utc : `${utc}Z`);
    if (Number.isNaN(parsed.getTime())) {
      return utc;
    }

    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hourCycle: 'h23',
    }).format(parsed);
  }
}
