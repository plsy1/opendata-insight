import { Injectable } from '@angular/core';

interface PerformerOrder {
  [listKey: string]: string[];  // listKey -> ordered names
}

@Injectable({ providedIn: 'root' })
export class PerformerOrderService {
  private static readonly STORAGE_KEY = 'performer-card-order';

  /** Get persisted order for a list, returns null if none saved */
  getOrder(listKey: string): string[] | null {
    try {
      const raw = localStorage.getItem(PerformerOrderService.STORAGE_KEY);
      if (raw) {
        const all: PerformerOrder = JSON.parse(raw);
        return all[listKey] || null;
      }
    } catch { /* ignore */ }
    return null;
  }

  /** Save current order for a list */
  saveOrder(listKey: string, names: string[]): void {
    try {
      const raw = localStorage.getItem(PerformerOrderService.STORAGE_KEY);
      const all: PerformerOrder = raw ? JSON.parse(raw) : {};
      all[listKey] = names;
      localStorage.setItem(PerformerOrderService.STORAGE_KEY, JSON.stringify(all));
    } catch { /* ignore */ }
  }

  /** Apply saved order to an array, preserving new items at the end */
  applySavedOrder<T extends { name: string }>(listKey: string, items: T[]): T[] {
    const saved = this.getOrder(listKey);
    if (!saved) return items;

    const map = new Map<string, T>();
    items.forEach(item => map.set(item.name, item));

    const ordered: T[] = [];
    // Add items in saved order
    for (const name of saved) {
      const item = map.get(name);
      if (item) {
        ordered.push(item);
        map.delete(name);
      }
    }
    // Append any new items not in saved order
    map.forEach(item => ordered.push(item));

    return ordered;
  }
}
