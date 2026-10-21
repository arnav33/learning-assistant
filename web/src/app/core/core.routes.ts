import { Routes } from '@angular/router';
import { Agent } from './agent/agent';
import { Model } from './model/model';

export const routes: Routes = [
  {
    path: 'model',
    component: Model
  },
  {
    path: 'agent',
    component: Agent
  }
];