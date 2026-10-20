import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: 'core',
        loadChildren: () => import('./core/core.routes').then((m) => m.routes)
    }
];
