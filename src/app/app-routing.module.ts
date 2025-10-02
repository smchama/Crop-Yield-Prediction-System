import { PredictionComponent } from './prediction/prediction.component';

import { UsersComponent } from './users/users.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { LoginComponent } from './login/login.component';
import { MenuComponent } from './menu/menu.component';


const routes: Routes = [
  { path: "login", component: LoginComponent },
  { path: "", redirectTo: "/login", pathMatch: "full" },
  {
    path: "menu",
    component: MenuComponent,
    children: [
      { path: "dashboard", component: DashboardComponent },
      { path: "users", component: UsersComponent },
      { path: "prediction", component: PredictionComponent },

    ],
    runGuardsAndResolvers: "always"
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { onSameUrlNavigation: "reload" })],
  exports: [RouterModule]
})
export class AppRoutingModule {}
export const routingComponents = [];
